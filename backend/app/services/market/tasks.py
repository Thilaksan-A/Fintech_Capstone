from celery import shared_task
from app.services.market import (
    sync_binance_crypto_market_information,
    sync_crypto_asset_with_coingecko,
    sync_top_coingecko_crypto_metadata,
)

import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name='market.sync_binance_crypto_market_information_task',
)
def sync_binance_crypto_market_information_task(self):
    """
    Task to sync Binance crypto market information.
    """
    try:
        sync_binance_crypto_market_information()
        logger.info("Successfully synced Binance crypto market information.")
    except Exception as exc:
        logger.error(f"Error syncing Binance crypto market information: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True, name='market.sync_crypto_asset_with_coingecko_task')
def sync_crypto_asset_with_coingecko_task(self):
    """
    Task to sync crypto assets with Coingecko.
    """
    try:
        sync_crypto_asset_with_coingecko()
        logger.info("Successfully synced crypto assets with Coingecko.")
    except Exception as exc:
        logger.error(f"Error syncing crypto assets with Coingecko: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True, name='market.sync_top_coingecko_crypto_metadata_task')
def sync_top_coingecko_crypto_metadata_task(self):
    """
    Task to sync top Coingecko crypto metadata.
    """
    try:
        sync_top_coingecko_crypto_metadata()
        logger.info("Successfully synced top Coingecko crypto metadata.")
    except Exception as exc:
        logger.error(f"Error syncing top Coingecko crypto metadata: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)
