from unittest.mock import MagicMock, patch

from app.schemas.youtube_schema import YoutubeCommentInfo
from app.services.sentiment.youtube import youtube_filter
from app.services.sentiment.youtube.youtube_filter import (
    check_author_patterns,
    check_comment_characteristics,
    check_spam_patterns,
    create_comment_fingerprint,
    exclude_bot_comments,
    filter_crypto_comments,
    filter_english_comments,
    filter_unique_comments,
    get_crypto_asset_patterns,
    is_bot_comment,
    is_english_comment,
    sanitise_comments,
)

from tests.factories.crypto import (
    CryptoAssetFactory,
    CryptoMarketDataFactory,
    CryptoSourceFactory,
)
from langdetect.lang_detect_exception import LangDetectException


def test_create_comment_fingerprint(subtests):
    cases = [
        ("basic", "Hello, world!", "hello world"),
        ("reordered", "Spam is bad!", "bad is spam"),
        ("reordered2", "bad spam is.", "bad is spam"),
        ("normalization", "  Hello   WORLD!!!  ", "hello world"),
    ]
    for desc, text, expected in cases:
        with subtests.test(msg=desc):
            assert create_comment_fingerprint(text) == expected


def test_check_spam_patterns(subtests):
    cases = [
        ("no spam", "This is a normal comment.", 0.0),
        ("subscribe back", "Subscribe back to my channel!", 0.3),
        ("check out channel", "Check out my channel for more videos!", 0.3),
        ("make money", "Make money fast with this amazing opportunity!", 0.3),
        ("bot mention", "This is an automated bot script.", 0.3),
        ("only special chars", "!!!@@@###", 0.3),
        ("first/early", "First! I love this video.", 0.3),
        ("url", "Check this out: https://spam.com", 0.3),
        ("visit link", "Visit my website link for more info!", 0.3),
        ("subscribe channel", "Subscribe to my channel!", 0.3),
        (
            "multiple patterns",
            "Subscribe and check out my channel! Click here: http://spam.com",
            0.8,
        ),
    ]
    for desc, text, expected in cases:
        with subtests.test(msg=desc):
            score = check_spam_patterns(text)
            if expected == 0.8:
                assert score == expected
            else:
                assert 0.0 <= score <= 0.8
                if expected > 0.0:
                    assert score > 0.0


def test_get_crypto_asset_patterns():
    # Create some assets in the test DB
    asset1 = CryptoAssetFactory(symbol="BTC", name="Bitcoin", ranking=1)
    asset2 = CryptoAssetFactory(symbol="ETH", name="Ethereum", ranking=2)
    source_binance = CryptoSourceFactory(name="Binance")
    CryptoMarketDataFactory(
        asset=asset1,
        source=source_binance,
    )
    CryptoMarketDataFactory(
        asset=asset2,
        source=source_binance,
    )

    patterns = get_crypto_asset_patterns(2)
    symbols = [p.symbol for p in patterns]
    assert "BTC" in symbols
    assert "ETH" in symbols

    btc_pattern = next(p for p in patterns if p.symbol == "BTC")
    eth_pattern = next(p for p in patterns if p.symbol == "ETH")

    # Should match symbol and name, case-insensitive, with punctuation/possessive
    assert btc_pattern.pattern.search("BTC")
    assert btc_pattern.pattern.search("btc's")
    assert btc_pattern.pattern.search("Bitcoin!")
    assert not btc_pattern.pattern.search("notacoin")
    assert eth_pattern.pattern.search("Ethereum")
    assert eth_pattern.pattern.search("ETH,")
    assert not eth_pattern.pattern.search("meth is good")


def make_comment(text, author="User1234"):
    c = YoutubeCommentInfo(
        text=text,
        author=author,
        like_count=0,
        reply_count=0,
        video_id="video123",
        comment_id="comment123",
        author_channel_id="authorChan123",
        published_at="2025-07-28T12:00:00Z",
        updated_at="2025-07-28T12:01:00Z",
        crypto_mentions=[],
    )
    return c


def test_check_comment_characteristics(subtests):
    cases = [
        ("short", "ok", None, lambda score: score >= 0.2),
        ("all caps", "THIS IS SHOUTING", None, lambda score: score >= 0.2),
        ("punctuation", "Wow!! Amazing!!", None, lambda score: score >= 0.2),
        ("no words", "12345!!!", None, lambda score: score >= 0.4),
    ]
    for desc, text, emoji_count_val, assertion in cases:
        with subtests.test(msg=desc):
            comment = make_comment(text)
            if emoji_count_val is not None:
                orig = youtube_filter.emoji_count
                youtube_filter.emoji_count = (
                    lambda t, count=emoji_count_val: count
                )
                score = check_comment_characteristics(comment)
                youtube_filter.emoji_count = orig
            else:
                score = check_comment_characteristics(comment)
            assert assertion(score)


def test_check_comment_characteristics_emojis_patch(subtests):
    # Separate test for emoji_count patching
    comment = make_comment("😀😀😀 wow")
    from app.services.sentiment.youtube import youtube_filter

    orig = youtube_filter.emoji_count
    youtube_filter.emoji_count = lambda t: 3
    with subtests.test(msg="emojis"):
        score = check_comment_characteristics(comment)
        assert score >= 0.3
    youtube_filter.emoji_count = orig


def test_check_author_patterns(subtests):
    cases = [
        ("random digits", "User123456", lambda score: score >= 0.3),
        ("generic guest", "guest123", lambda score: score >= 0.2),
        ("generic visitor", "visitor9999", lambda score: score >= 0.2),
        ("letters+numbers", "abcdef12", lambda score: score >= 0.2),
        ("nonbot", "Alice", lambda score: score == 0.0),
    ]
    for desc, author, assertion in cases:
        with subtests.test(msg=desc):
            score = check_author_patterns(author)
            assert assertion(score)


@patch("app.services.sentiment.youtube.youtube_filter.check_spam_patterns")
@patch(
    "app.services.sentiment.youtube.youtube_filter.check_comment_characteristics",
)
@patch("app.services.sentiment.youtube.youtube_filter.check_author_patterns")
def test_is_bot_comment(mock_author, mock_chars, mock_spam, subtests):
    cases = [
        ("all low", 0.0, 0.0, 0.0, False, (0.0, 0.0)),
        ("spam only", 0.8, 0.0, 0.0, True, (0.5, 1.0)),
        ("chars only", 0.0, 0.8, 0.0, True, (0.5, 1.0)),
        ("author only", 0.0, 0.0, 0.5, False, (0.3, 0.5)),
        ("all moderate", 0.4, 0.4, 0.4, True, (0.5, 1.0)),
        ("score capped", 0.8, 0.8, 0.8, True, (1.0, 1.0)),
    ]
    for (
        desc,
        spam,
        chars,
        author,
        expected_is_bot,
        (min_score, max_score),
    ) in cases:
        with subtests.test(msg=desc):
            mock_spam.return_value = spam
            mock_chars.return_value = chars
            mock_author.return_value = author
            comment = make_comment("Test", author="User1234")
            is_bot, score = is_bot_comment(comment)
            assert is_bot == expected_is_bot
            assert min_score <= score <= max_score


@patch("app.services.sentiment.youtube.youtube_filter.detect")
def test_is_english_comment(mock_detect, subtests):
    cases = [
        ("short comment", "OK", None, True),
        ("english detected", "This is an English comment.", "en", True),
        ("non-english detected", "Ceci n'est pas anglais.", "fr", False),
        (
            "langdetect exception",
            "???",
            LangDetectException(
                code="langdetect_failed",
                message="langdetect failed",
            ),
            False,
        ),
    ]
    for desc, text, detect_return, expect_english in cases:
        with subtests.test(msg=desc):
            comment = make_comment(text)
            if isinstance(detect_return, Exception):
                mock_detect.side_effect = detect_return
            elif detect_return is not None:
                mock_detect.return_value = detect_return
            else:
                mock_detect.side_effect = None
            result = is_english_comment(comment)
            assert result == expect_english


@patch("app.services.sentiment.youtube.youtube_filter.is_bot_comment")
def test_exclude_bot_comments(mock_is_bot_comment, subtests):
    cases = [
        ("all human", [False, False], 2),
        ("all bot", [True, True], 0),
        ("mixed", [False, True, False], 2),
    ]
    for desc, is_bot_list, expected_count in cases:
        with subtests.test(msg=desc):
            comments = [
                make_comment(f"Comment {i}") for i in range(len(is_bot_list))
            ]
            # Each call to is_bot_comment returns (is_bot, bot_score)
            mock_is_bot_comment.side_effect = [
                (is_bot, 0.42) for is_bot in is_bot_list
            ]
            filtered = list(exclude_bot_comments(comments))
            assert len(filtered) == expected_count
            for c in filtered:
                assert hasattr(c, "bot_score")
                assert c.bot_score == 0.42


@patch("app.services.sentiment.youtube.youtube_filter.is_english_comment")
def test_filter_english_comments(mock_is_english_comment, subtests):
    cases = [
        ("all english", [True, True], 2),
        ("all non-english", [False, False], 0),
        ("mixed", [True, False, True], 2),
    ]
    for desc, is_english_list, expected_count in cases:
        with subtests.test(msg=desc):
            comments = [
                make_comment(f"Comment {i}")
                for i in range(len(is_english_list))
            ]
            mock_is_english_comment.side_effect = is_english_list
            filtered = list(filter_english_comments(comments))
            assert len(filtered) == expected_count


def test_filter_unique_comments(subtests):
    cases = [
        (
            "all unique",
            [make_comment("A"), make_comment("B"), make_comment("C")],
            3,
        ),
        (
            "all duplicates",
            [make_comment("A"), make_comment("A"), make_comment("A")],
            0,
        ),
        (
            "mixed",
            [
                make_comment("A"),
                make_comment("B"),
                make_comment("A"),
                make_comment("C"),
            ],
            2,
        ),
    ]
    for desc, comments, expected_count in cases:
        with subtests.test(msg=desc):
            filtered = list(filter_unique_comments(comments))
            assert len(filtered) == expected_count
            # All returned comments should be unique
            texts = [c.text for c in filtered]
            assert len(texts) == len(set(texts))


@patch(
    "app.services.sentiment.youtube.youtube_filter.get_crypto_asset_patterns",
)
def test_filter_crypto_comments(mock_get_patterns, subtests):
    # Fake asset pattern that matches "BTC" and "ETH"
    class FakePattern:
        def __init__(self, symbol):
            self.symbol = symbol
            self.pattern = MagicMock()
            self.pattern.search = lambda text: symbol in text

    mock_get_patterns.return_value = [FakePattern("BTC"), FakePattern("ETH")]

    cases = [
        (
            "all match",
            [make_comment("BTC to the moon!"), make_comment("ETH is great!")],
            2,
            ["BTC", "ETH"],
        ),
        (
            "none match",
            [make_comment("No crypto here."), make_comment("Still nothing.")],
            0,
            [],
        ),
        (
            "mixed",
            [
                make_comment("BTC to the moon!"),
                make_comment("No crypto here."),
                make_comment("ETH is great!"),
            ],
            2,
            ["BTC", "ETH"],
        ),
    ]
    for desc, comments, expected_count, expected_symbols in cases:
        with subtests.test(msg=desc):
            filtered = list(filter_crypto_comments(comments, ranking=10))
            assert len(filtered) == expected_count
            for c, symbol in zip(filtered, expected_symbols):
                assert symbol in c.crypto_mentions


@patch("app.services.sentiment.youtube.youtube_filter.exclude_bot_comments")
@patch("app.services.sentiment.youtube.youtube_filter.filter_english_comments")
@patch("app.services.sentiment.youtube.youtube_filter.filter_unique_comments")
@patch("app.services.sentiment.youtube.youtube_filter.filter_crypto_comments")
def test_sanitise_comments_pipeline(
    mock_filter_crypto,
    mock_filter_unique,
    mock_filter_english,
    mock_exclude_bot,
    subtests,
):
    c1 = make_comment("BTC to the moon!", author="Alice")
    c2 = make_comment("ETH is great!", author="Bob")
    comments = [c1, c2]

    # Each filter returns the same comments (simulate no filtering)
    mock_exclude_bot.side_effect = lambda x: iter(comments)
    mock_filter_english.side_effect = lambda x: iter(comments)
    mock_filter_unique.side_effect = lambda x: iter(comments)
    mock_filter_crypto.side_effect = lambda x, ranking: iter(comments)

    result = sanitise_comments(comments, ranking=10)
    assert result == comments

    # Now simulate each filter removing one comment
    mock_exclude_bot.side_effect = lambda x: iter([c1, c2])
    mock_filter_english.side_effect = lambda x: iter([c1])
    mock_filter_unique.side_effect = lambda x: iter([c1])
    mock_filter_crypto.side_effect = lambda x, ranking: iter([c1])

    result = sanitise_comments(comments, ranking=10)
    assert result == [c1]

    # Simulate all comments filtered out
    mock_exclude_bot.side_effect = lambda x: iter([])
    mock_filter_english.side_effect = lambda x: iter([])
    mock_filter_unique.side_effect = lambda x: iter([])
    mock_filter_crypto.side_effect = lambda x, ranking: iter([])

    result = sanitise_comments(comments, ranking=10)
    assert result == []
