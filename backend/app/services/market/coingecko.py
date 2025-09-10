import logging
import requests
import app.env
from app.models.crypto import (
    CryptoAsset,
    CryptoCoingeckoSentimentData,
    CryptoMarketData,
)
from time import sleep
from app.extensions import db
from app.services.market.constants import (
    COINGECKO_BASE_URL,
    STABLECOIN_SYMBOLS,
)
from app.constants import TOP_CRYPTOCURRENCIES_LIMIT
from app.utils.decorators import transactional
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


FETCH_METADATA_INTERVAL_S = 4


def fetch_coingecko_market_data(
    vs_currency="usd",
    per_page=TOP_CRYPTOCURRENCIES_LIMIT,
):
    """
    Fetch market data from Coingecko for the top N coins.
    Returns a list of currency data dictionaries or an empty list on failure.
    """
    try:
        url = f"{COINGECKO_BASE_URL}/coins/markets"
        params = {
            "order": "market_cap_desc",
            "vs_currency": vs_currency,
            "per_page": per_page,
        }
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(
            f"Coingecko API error: failed to fetch market data. Error: {e}",
        )
        return []


@transactional
def sync_crypto_asset_with_coingecko():
    """
    Fetch and store top cryptocurrencies from Coingecko, excluding stablecoins.
    """
    currency_data = fetch_coingecko_market_data()

    logger.info("Coingecko rankings script: Writing data to SQLAlchemy")

    rank_deducter = 0
    for curr in currency_data:
        if curr["symbol"] in STABLECOIN_SYMBOLS:
            logger.info(f"Skipped coin {curr['symbol']}")
            rank_deducter += 1
            continue

        asset = CryptoAsset(
            symbol=curr.get('symbol', '').upper(),
            name=curr.get('name', ''),
            ranking=curr.get('market_cap_rank', 1) - rank_deducter,
            image=curr.get('image', ''),
            coingecko_id=curr.get('id'),
            marketcap=curr.get('market_cap'),
            volume=curr.get('total_volume'),
        )
        db.session.merge(asset)

    logger.info("Coingecko rankings script: Done writing.")


@transactional
def sync_top_coingecko_crypto_metadata():
    """
    Updates metadata for top-ranked cryptocurrencies.
    """
    query = (
        select(CryptoAsset)
        .distinct()
        .join(CryptoMarketData, CryptoAsset.symbol == CryptoMarketData.symbol)
        .order_by(CryptoAsset.ranking)
        .limit(TOP_CRYPTOCURRENCIES_LIMIT)
    )
    cryptocurrencies = db.session.execute(query).scalars().all()
    logger.info(f"Metadata: Updating {len(cryptocurrencies)} coins")

    for crypto in cryptocurrencies:
        records = fetch_coingecko_metadata(crypto)
        for rec in records:
            db.session.merge(rec)
        sleep(FETCH_METADATA_INTERVAL_S)
    logger.info("Metadata: Done writing to DB.")


def fetch_coingecko_metadata(crypto: CryptoAsset) -> list:
    """
    Fetch enriched metadata for a given cryptocurrency from Coingecko.
    Returns a list of model instances to be persisted.
    """
    if not crypto.coingecko_id:
        logger.info(f"Metadata: Skipping {crypto.name}, missing Coingecko ID")
        return []

    logger.info(f"Metadata: Fetching for {crypto.name}")

    headers = {
        "x-cg-demo-api-key": app.env.COINGECKO_API_KEY,
        "accept": "application/json",
    }

    try:
        url = f"{COINGECKO_BASE_URL}/coins/{crypto.coingecko_id}?market_data=false"
        response = requests.get(url, headers=headers)
        data = response.json()

        # Parse categories
        categories = ", ".join(data.get("categories", []))

        # Filter trusted purchase platforms
        platforms = {
            ticker.get("market", {}).get("name")
            for ticker in data.get("tickers", [])
            if ticker.get("trust_score") == "green"
            and ticker.get("market", {}).get("name")
        }
        purchase_platforms = ", ".join(platforms)

        return [
            CryptoAsset(
                symbol=crypto.symbol,
                ranking=crypto.ranking,
                name=crypto.name,
                description=data.get("description", {}).get(
                    "en",
                    "No Content Found",
                ),
                categories=categories,
                homepage_url=data.get("links", {}).get("homepage", [""])[0],
                subreddit_url=data.get("links", {}).get("subreddit_url", ""),
                purchase_platforms=purchase_platforms,
            ),
            CryptoCoingeckoSentimentData(
                symbol=crypto.symbol,
                sentiment_up_percentage=data.get(
                    "sentiment_votes_up_percentage",
                    0.0,
                ),
                sentiment_down_percentage=data.get(
                    "sentiment_votes_down_percentage",
                    0.0,
                ),
                reddit_average_posts_48h=data.get(
                    "reddit_average_posts_48h",
                    0.0,
                ),
                commit_count_4_weeks=data.get("commit_count_4_weeks", 0),
            ),
        ]

    except Exception as e:
        logger.error(f"Metadata: Error fetching {crypto.name} — {e}")
        return []
