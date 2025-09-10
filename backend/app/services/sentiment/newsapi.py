from datetime import datetime, timezone, timedelta
from typing import List
import requests
import html
import re
from bs4 import BeautifulSoup
from app.models.crypto import CryptoAsset, CryptoNewsData, CryptoMarketData
from app.extensions import db
from app.env import NEWS_API_KEY
from app.constants import TOP_CRYPTOCURRENCIES_LIMIT
from app.utils.decorators import transactional
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

import logging

logger = logging.getLogger(__name__)


def clean_content(content: str) -> str:
    """Clean the content by removing HTML tags, multiple spaces, and URLs."""
    if not content:
        return ''

    content = html.unescape(content)
    soup = BeautifulSoup(content, 'html.parser')
    content = soup.get_text()
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'https?://\S+|www\.\S+', '', content)
    return content


def fetch_news_api_data(
    from_date: datetime, query: str, **extra_request_params
) -> List[dict]:
    """Fetch news data from API for a specific crypto asset."""
    formatted_date = from_date.strftime('%Y-%m-%d')
    logger.info(
        f"Fetching news data for query: {query} from date: {formatted_date}",
    )

    # Base parameters
    params = {
        'q': query,
        'from': formatted_date,
        'language': 'en',
        'apiKey': NEWS_API_KEY,
        **extra_request_params,
    }

    try:
        response = requests.get(
            'https://newsapi.org/v2/everything',
            params=params,
        )
        if not response.ok:
            logger.error(
                f"Failed to fetch news data for {query}: {response.status_code}",
            )
            return []

        data = response.json()
        articles = data.get('articles', [])
        logger.info(f"Found {len(articles)} articles for query: {query}")
        return articles
    except Exception as e:
        logger.error(f"Error fetching news data for {query}: {e}")
        return []


@transactional
def store_news_data(symbol: str, articles: List[dict]):
    """Store news articles in the database, skipping duplicates."""
    values = []
    for article in articles:
        values.append(
            {
                'symbol': symbol,
                'timestamp': article.get('publishedAt', ''),
                'description': article.get('description', '')
                or 'No description available',
                'title': article.get('title', ''),
                'source_url': article.get('url', ''),
                'url_image': article.get('urlToImage', '') or '',
                'content': clean_content(article.get('content', ''))
                or 'No content available',
            },
        )
    stmt = insert(CryptoNewsData).values(values)
    stmt = stmt.on_conflict_do_nothing(
        index_elements=['symbol', 'timestamp', 'source_url'],
    )
    db.session.execute(stmt)
    db.session.commit()


def fetch_and_store_crypto_news(
    from_date: datetime,
    crypto_asset: CryptoAsset,
):
    """Fetch and store news data for a specific crypto asset."""
    articles = fetch_news_api_data(from_date, query=crypto_asset.name)
    if articles:
        store_news_data(crypto_asset.symbol, articles)


@transactional
def collect_crypto_news():
    """Fetch news data for top-ranked cryptocurrencies."""
    logger.info("Collecting crypto news data")
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    query = (
        select(CryptoAsset)
        .distinct()
        .join(CryptoMarketData, CryptoAsset.symbol == CryptoMarketData.symbol)
        .order_by(CryptoAsset.ranking)
        .limit(TOP_CRYPTOCURRENCIES_LIMIT)
    )
    cryptocurrencies = db.session.execute(query).scalars().all()
    for asset in cryptocurrencies:
        fetch_and_store_crypto_news(yesterday, asset)
    logger.info("Finished collecting crypto news data")
