import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class EnvironmentError(Exception):
    """Raised when required environment variables are missing."""

    pass


def get_required_env(key: str, description: str = None) -> str:
    value = os.getenv(key)
    if not value:
        desc = description or f"Environment variable '{key}'"
        raise EnvironmentError(f"{desc} is required but not set")
    return value


def get_optional_env(key: str, default: str) -> str:

    env = os.getenv(key)
    if not env:
        logger.warning(
            f"Environment variable '{key}' not set, using default: {default}",
        )
        return default
    return env


# Required envs
try:
    JWT_SECRET_KEY = get_required_env(
        'JWT_SECRET_KEY',
        'JWT_SECRET_KEY (for JWT authentication)',
    )

    FLASK_ENV = get_optional_env('FLASK_ENV', 'development')

    if FLASK_ENV.lower() == 'local':
        DATABASE_URL = get_required_env(
            'LOCAL_DATABASE_URL',
            'LOCAL_DATABASE_URL (for local development)',
        )
    else:
        DATABASE_URL = get_required_env(
            'DATABASE_URL',
            'DATABASE_URL (for production)',
        )

    # Testing database (only required when testing)
    TESTING_DATABASE_URL = get_required_env('TESTING_DATABASE_URL')

    # Celery configuration
    CELERY_BROKER_URL = get_required_env(
        'CELERY_BROKER_URL',
        'CELERY_BROKER_URL (for Celery)',
    )
    CELERY_RESULT_BACKEND = get_required_env(
        'CELERY_RESULT_BACKEND',
        'CELERY_RESULT_BACKEND (for Celery)',
    )

    # Reddit API credentials (required for Reddit functionality)
    REDDIT_CLIENT_ID = get_required_env(
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_ID (for Reddit API)',
    )
    REDDIT_CLIENT_SECRET = get_required_env(
        'REDDIT_CLIENT_SECRET',
        'REDDIT_CLIENT_SECRET (for Reddit API)',
    )
    REDDIT_USER_AGENT = get_required_env(
        'REDDIT_USER_AGENT',
        'REDDIT_USER_AGENT (for Reddit API)',
    )
    COINGECKO_API_KEY = get_optional_env(
        'COINGECKO_API_KEY',
        'COINGECKO_API_KEY (for Coingecko API)',
    )
    NEWS_API_KEY = get_optional_env(
        'NEWS_API_KEY',
        'NEWS_API_KEY (for News API)',
    )
    NEWS_API_KEY_FRONTEND = get_optional_env(
        'NEWS_API_KEY_FRONTEND',
        '(unique News API key reserved for on demand news for frontend)',
    )
    YOUTUBE_API_KEY = get_optional_env(
        'YOUTUBE_API_KEY',
        'YOUTUBE_API_KEY (for YouTube API)',
    )
    GEMINI_API_KEY = get_optional_env(
        'GEMINI_API_KEY',
        'GEMINI_API_KEY (for Gemini API)',
    )

    YOUTUBE_API_KEY = get_required_env(
        'YOUTUBE_API_KEY',
        'YOUTUBE_API_KEY (for YouTube API)',
    )

except EnvironmentError as e:
    logger.error(f"Configuration Error: {e}")
    logger.info(
        "Please check your .env file and ensure all required variables are set.",
    )
    raise SystemExit(1)  # Exit the program if required variables are missing


# Optional envs
ENABLE_TIMESCALE_INIT = get_optional_env(
    'ENABLE_TIMESCALE_INIT',
    'false',
).lower() in ['1', 'true', 'yes']


__all__ = [
    'DATABASE_URL',
    'TESTING_DATABASE_URL',
    'JWT_SECRET_KEY',
    'FLASK_ENV',
    'ENABLE_TIMESCALE_INIT',
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT',
    'COINGECKO_API_KEY',
]
