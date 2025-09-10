import pytest
from unittest.mock import patch, MagicMock
from app.services.sentiment.reddit import (
    preprocess_text,
    fetch_reddit_data_for_currency,
    fetch_reddit_data_concurrent,
    collect_reddit_crypto_discussions,
)
from app.models.crypto import CryptoAsset, CryptoSource, CryptoRedditData
from datetime import datetime, timezone
from tests.factories.crypto import (
    CryptoAssetFactory,
    CryptoSourceFactory,
    CryptoMarketDataFactory,
)


@pytest.fixture(scope="function")
def init_reddit_data():
    asset1 = CryptoAssetFactory(
        symbol="BTC",
        name="bitcoin",
        ranking=1,
        coingecko_id="bitcoin",
    )
    asset2 = CryptoAssetFactory(
        symbol="ETH",
        name="ethereum",
        ranking=2,
        coingecko_id="ethereum",
    )
    source_binance = CryptoSourceFactory(name="Binance")
    CryptoMarketDataFactory(
        asset=asset1,
        source=source_binance,
    )
    CryptoMarketDataFactory(
        asset=asset2,
        source=source_binance,
    )

    if (
        CryptoSource.query.filter(CryptoSource.name == "reddit").first()
        is None
    ):
        CryptoSourceFactory(
            name="reddit",
            type="social",
        )

    yield


@patch('app.services.sentiment.reddit.SAFE_TEXT_LENGTH', 1897)
def test_preprocess_text(subtests):
    cases = [
        {
            "input": "Check out this link: [Reddit](https://reddit.com) and https://example.com",
            "expected_substrings": ["Check out this link:"],
            "unexpected_substrings": [
                "https://reddit.com",
                "https://example.com",
                "Reddit",
            ],
            "expected": None,
        },
        {
            "input": "",
            "expected": "",
            "expected_substrings": [],
            "unexpected_substrings": [],
        },
        {
            "input": None,
            "expected": "",
            "expected_substrings": [],
            "unexpected_substrings": [],
        },
        {
            "input": "A" * 3000,  # Text longer than max_bytes limit
            "expected": None,
            "expected_substrings": [
                "...",
            ],  # Should be truncated with ellipsis
            "unexpected_substrings": [],
        },
        {
            "input": "Short text",
            "expected": "Short text",
            "expected_substrings": [],
            "unexpected_substrings": ["..."],  # Should NOT be truncated
        },
        {
            "input": "Bitcoin with emoji 🚀 and unicode ñáéíóú",
            "expected": None,
            "expected_substrings": ["Bitcoin with emoji 🚀 and unicode ñáéíóú"],
            "unexpected_substrings": ["..."],  # Should NOT be truncated
        },
        {
            "input": "Text with\nmultiple\nlines\nand\tspecial\rcharacters",
            "expected": None,
            "expected_substrings": ["Text with", "multiple", "lines"],
            "unexpected_substrings": ["..."],  # Should NOT be truncated
        },
    ]

    for case in cases:
        with subtests.test(
            msg=str(case["input"])[:50] + "..."
            if case["input"] and len(str(case["input"])) > 50
            else str(case["input"]),
        ):
            clean_text = preprocess_text(case["input"])

            if case["expected"] is not None:
                assert clean_text == case["expected"]

            for substr in case.get("expected_substrings", []):
                assert (
                    substr in clean_text
                ), f"Expected substring '{substr}' not found in '{clean_text}'"

            for substr in case.get("unexpected_substrings", []):
                assert (
                    substr not in clean_text
                ), f"Unexpected substring '{substr}' found in '{clean_text}'"

            # Test that result is within safe byte limits
            encoded_result = clean_text.encode('utf-8')
            assert (
                len(encoded_result) <= 2000
            ), f"Text too long: {len(encoded_result)} bytes"


@patch('app.services.sentiment.reddit.SAFE_TEXT_LENGTH', 1897)
def test_preprocess_text_truncation_edge_cases():
    """Test edge cases for text truncation functionality."""

    # Test UTF-8 character boundary handling
    utf8_text = "Bitcoin " + "🚀" * 1000  # Emoji characters (4 bytes each)
    clean_text = preprocess_text(utf8_text)

    # Should be truncated but not break UTF-8 characters
    assert clean_text.endswith("...")
    assert len(clean_text.encode('utf-8')) <= 2000

    # Test that truncated text is still valid UTF-8
    try:
        clean_text.encode('utf-8')
    except UnicodeEncodeError:
        pytest.fail("Truncated text contains invalid UTF-8 characters")

    # Test with exactly at the limit
    clean_text = preprocess_text("A" * 1897)
    assert len(clean_text.encode('utf-8')) <= 2000
    assert not clean_text.endswith("...")

    # Test with mixed ASCII and Unicode
    mixed_text = "Bitcoin is great! " + "ñ" * 2000  # Mix ASCII and Unicode
    clean_text = preprocess_text(mixed_text)
    assert clean_text.endswith("...")
    assert len(clean_text.encode('utf-8')) <= 2000
    assert "Bitcoin is great!" in clean_text


@patch('app.services.sentiment.reddit.SAFE_TEXT_LENGTH', 1897)
def test_preprocess_text_with_special_characters():
    """Test with various special characters and formatting."""
    text_with_special = "Bitcoin™ is great! 💰 Check: https://bitcoin.org and [link](https://test.com)"
    clean_text = preprocess_text(text_with_special)

    assert "Bitcoin™ is great! 💰 Check:" in clean_text
    assert "https://bitcoin.org" not in clean_text
    assert "https://test.com" not in clean_text
    # The regex removes the entire markdown link including the text
    assert "link" not in clean_text

    # Ensure it's within byte limits
    assert len(clean_text.encode('utf-8')) <= 2000


@patch('app.services.sentiment.reddit.create_reddit_client')
def test_fetch_reddit_data_for_currency(mock_reddit_client, init_reddit_data):
    # Mock Reddit API objects
    mock_submission = MagicMock()
    mock_submission.title = "Bitcoin is amazing!"
    mock_submission.selftext = "I love BTC"
    mock_submission.score = 100

    mock_comment = MagicMock()
    mock_comment.body = "Great post about Bitcoin!"
    mock_comment.score = 50

    mock_submission.comments.list.return_value = [mock_comment]
    mock_submission.comments.replace_more = MagicMock()

    mock_subreddit = MagicMock()
    mock_subreddit.search.return_value = [mock_submission]

    mock_reddit_instance = MagicMock()
    mock_reddit_instance.subreddit.return_value = mock_subreddit
    mock_reddit_client.return_value = mock_reddit_instance

    # Get test data
    currencies = CryptoAsset.query.all()
    btc_currency = next(c for c in currencies if c.symbol == "BTC")
    source_id = (
        CryptoSource.query.filter(CryptoSource.name == "reddit").first().id
    )
    timestamp = datetime.now(timezone.utc)

    # Test the function
    data = fetch_reddit_data_for_currency(
        btc_currency,
        "CryptoCurrency",
        "hour",
        currencies,
        timestamp,
        source_id,
    )

    assert len(data) >= 2  # At least submission + comment
    assert any(d.symbol == "BTC" for d in data)
    assert any("Bitcoin is amazing!" in d.text for d in data)


@patch('app.services.sentiment.reddit.store_reddit_data')
@patch('app.services.sentiment.reddit.fetch_reddit_data_for_currency')
@patch('app.constants.TOP_CRYPTOCURRENCIES_LIMIT', 2)
def test_fetch_reddit_data_concurrent_success(
    mock_fetch_data,
    mock_store_data,
    init_reddit_data,
):
    # Mock return values
    mock_fetch_data.return_value = [
        CryptoRedditData(
            symbol="BTC",
            text="Test",
            subreddit="test",
            source_id=1,
            votes=1,
            confidence=1.0,
            timestamp=datetime.now(),
        ),
    ]

    fetch_reddit_data_concurrent(subreddits=["CryptoCurrency"], max_workers=1)
    assert mock_fetch_data.call_count == 2
    assert mock_store_data.call_count == 1


@patch('app.services.sentiment.reddit.store_reddit_data')
@patch('app.services.sentiment.reddit.fetch_reddit_data_for_currency')
@patch('app.constants.TOP_CRYPTOCURRENCIES_LIMIT', 1)
def test_fetch_reddit_data_concurrent_no_data(
    mock_fetch_data,
    mock_store_data,
    init_reddit_data,
):
    mock_fetch_data.return_value = []  # No data returned

    fetch_reddit_data_concurrent(subreddits=["CryptoCurrency"], max_workers=1)

    assert mock_fetch_data.call_count == 2
    mock_store_data.assert_not_called()  # Should not store if no data


@patch('app.services.sentiment.reddit.fetch_reddit_data_concurrent')
def test_execute_reddit_data_task(mock_fetch_concurrent):
    collect_reddit_crypto_discussions(["CryptoCurrency"], "day", 10)
    mock_fetch_concurrent.assert_called_once()


@patch('app.services.sentiment.reddit.fetch_reddit_data_for_currency')
@patch('app.constants.TOP_CRYPTOCURRENCIES_LIMIT', 1)
def test_fetch_reddit_data_concurrent_exception_handling(
    mock_fetch_data,
    init_reddit_data,
):
    mock_fetch_data.side_effect = Exception("Reddit API error")

    # Should not raise exception, just log it
    fetch_reddit_data_concurrent(subreddits=["CryptoCurrency"], max_workers=1)

    assert mock_fetch_data.call_count == 2


@patch('app.services.sentiment.reddit.create_reddit_client')
def test_fetch_reddit_data_for_currency_exception_handling(
    mock_reddit_client,
    init_reddit_data,
):
    # Mock Reddit client to raise an exception
    mock_reddit_client.side_effect = Exception("Reddit API connection failed")

    # Get test data
    currencies = CryptoAsset.query.all()
    btc_currency = next(c for c in currencies if c.symbol == "BTC")
    source_id = (
        CryptoSource.query.filter(CryptoSource.name == "reddit").first().id
    )
    timestamp = datetime.now(timezone.utc)

    with pytest.raises(Exception, match="Reddit API connection failed"):
        fetch_reddit_data_for_currency(
            btc_currency,
            "CryptoCurrency",
            "hour",
            currencies,
            timestamp,
            source_id,
        )
