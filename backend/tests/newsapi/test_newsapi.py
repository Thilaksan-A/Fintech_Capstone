from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

import factory
from app.services.sentiment.newsapi import (
    clean_content,
    collect_crypto_news,
    fetch_news_api_data,
    fetch_and_store_crypto_news,
    store_news_data,
)
from app.models.crypto import CryptoNewsData
from tests.factories.crypto import (
    CryptoAssetFactory,
    CryptoMarketDataFactory,
    CryptoSourceFactory,
)


def test_clean_content():
    dirty = "<p>Hello <b>world</b>! Visit https://test.com</p>"
    clean = clean_content(dirty)
    assert clean == "Hello world! Visit "


def test_clean_content_empty():
    assert clean_content('') == ''
    assert clean_content(None) == ''


@patch('app.services.sentiment.newsapi.requests.get', autospec=True)
def test_fetch_news_api_data_success(mock_requests_get):
    # Mock API response
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {
        'articles': [
            {
                'title': 'Test Bitcoin News',
                'publishedAt': '2024-01-01T00:00:00Z',
                'description': 'desc',
                'url': 'url',
                'urlToImage': 'img',
                'content': 'content',
            },
        ],
    }
    mock_requests_get.return_value = mock_response

    from_date = datetime(2024, 1, 1)
    articles = fetch_news_api_data(from_date, "Bitcoin")

    assert len(articles) == 1
    assert articles[0]['title'] == 'Test Bitcoin News'


@patch('app.services.sentiment.newsapi.requests.get', autospec=True)
def test_fetch_news_api_data_non_200(mock_requests_get):
    # Mock non-200 response
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    from_date = datetime(2024, 1, 1)
    articles = fetch_news_api_data(from_date, "Bitcoin")

    assert articles == []


@patch('app.services.sentiment.newsapi.requests.get', autospec=True)
def test_fetch_news_api_data_exception(mock_requests_get):
    mock_requests_get.side_effect = Exception("Network error")

    from_date = datetime(2024, 1, 1)
    articles = fetch_news_api_data(from_date, "Bitcoin")

    assert articles == []


def test_store_news_data():
    # Setup mock DB
    CryptoAssetFactory.create(
        symbol='BTC',
        name='Bitcoin',
        ranking=1,
        coingecko_id='bitcoin',
    )
    articles = [
        {
            'publishedAt': '2024-01-01T00:00:00Z',
            'description': 'desc',
            'title': 'title',
            'url': 'url',
            'urlToImage': 'img',
            'content': 'content',
        },
    ]

    store_news_data('BTC', articles)

    # Verify CryptoNewsData was created
    assert CryptoNewsData.query.count() == 1
    news_data = CryptoNewsData.query.first()
    assert news_data.symbol == 'BTC'
    assert news_data.timestamp == datetime(2024, 1, 1, 0, 0)
    assert news_data.description == 'desc'
    assert news_data.title == 'title'
    assert news_data.source_url == 'url'
    assert news_data.url_image == 'img'
    assert news_data.content == 'content'


@patch('app.services.sentiment.newsapi.store_news_data')
@patch('app.services.sentiment.newsapi.fetch_news_api_data')
def test_fetch_and_store_crypto_news_success(
    mock_fetch_news_api_data,
    mock_store_news_data,
):
    # Mock crypto asset
    mock_crypto_asset = MagicMock()
    mock_crypto_asset.name = 'Bitcoin'
    mock_crypto_asset.symbol = 'BTC'

    # Mock successful API response
    mock_fetch_news_api_data.return_value = [
        {'title': 'Test', 'content': 'content'},
    ]

    from_date = datetime(2024, 1, 1)
    fetch_and_store_crypto_news(from_date, mock_crypto_asset)

    mock_fetch_news_api_data.assert_called_once_with(
        from_date,
        query='Bitcoin',
    )
    mock_store_news_data.assert_called_once_with(
        'BTC',
        [{'title': 'Test', 'content': 'content'}],
    )


@patch('app.services.sentiment.newsapi.store_news_data')
@patch('app.services.sentiment.newsapi.fetch_news_api_data')
def test_fetch_and_store_crypto_news_no_articles(
    mock_fetch_news_api_data,
    mock_store_news_data,
):
    # Mock crypto asset
    mock_crypto_asset = MagicMock()
    mock_crypto_asset.name = 'Bitcoin'
    mock_crypto_asset.symbol = 'BTC'

    # Mock empty API response
    mock_fetch_news_api_data.return_value = []

    from_date = datetime(2024, 1, 1)
    fetch_and_store_crypto_news(from_date, mock_crypto_asset)

    mock_fetch_news_api_data.assert_called_once_with(
        from_date,
        query='Bitcoin',
    )
    mock_store_news_data.assert_not_called()


@patch(
    'app.services.sentiment.newsapi.fetch_and_store_crypto_news',
    autospec=True,
)
@patch('app.services.sentiment.newsapi.datetime', autospec=True)
def test_execute_fetch_news_data_task(
    mock_datetime,
    mock_fetch_and_store_crypto_news,
):
    # Mock datetime
    mock_now = datetime(2024, 1, 2, tzinfo=timezone.utc)
    mock_datetime.now.return_value = mock_now

    crypto_assets = CryptoAssetFactory.create_batch(
        size=2,
        symbol=factory.Iterator(['BTC', 'ETH']),
        name=factory.Iterator(['Bitcoin', 'Ethereum']),
    )
    source_binance = CryptoSourceFactory(name="Binance")
    CryptoMarketDataFactory(
        asset=crypto_assets[0],
        source=source_binance,
    )
    CryptoMarketDataFactory(
        asset=crypto_assets[1],
        source=source_binance,
    )

    collect_crypto_news()

    # Verify fetch_and_store_crypto_news was called for each asset
    expected_yesterday = mock_now - timedelta(days=1)
    assert mock_fetch_and_store_crypto_news.call_count == 2
    mock_fetch_and_store_crypto_news.assert_any_call(
        expected_yesterday,
        crypto_assets[0],
    )
    mock_fetch_and_store_crypto_news.assert_any_call(
        expected_yesterday,
        crypto_assets[1],
    )


@patch('app.services.sentiment.newsapi.requests.get', autospec=True)
def test_fetch_news_api_data_with_extra_params(mock_requests_get):
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.json.return_value = {'articles': []}
    mock_requests_get.return_value = mock_response

    from_date = datetime(2024, 1, 1)
    fetch_news_api_data(
        from_date,
        "Bitcoin",
        sortBy="publishedAt",
        pageSize=50,
    )

    # Verify the extra params were passed in the request
    call_args = mock_requests_get.call_args
    params = call_args[1]['params']
    assert params['sortBy'] == 'publishedAt'
    assert params['pageSize'] == 50
    assert params['q'] == 'Bitcoin'
