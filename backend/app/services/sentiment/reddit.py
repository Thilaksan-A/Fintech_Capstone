import logging
import time
import praw
from app.config import Config
import re
import threading
from datetime import datetime, timezone
from app.models.crypto import (
    CryptoAsset,
    CryptoRedditData,
    CryptoSource,
    CryptoMarketData,
)
from app.extensions import db
from typing import List
from sqlalchemy.dialects.postgresql import insert
from app.env import REDDIT_CLIENT_ID, REDDIT_USER_AGENT, REDDIT_CLIENT_SECRET
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import scoped_session, sessionmaker
from app.utils import model_to_dict

from app.constants import TOP_CRYPTOCURRENCIES_LIMIT

logger = logging.getLogger(__name__)

# Global variables for thread-safe operations
submission_set = set()
submission_set_lock = threading.Lock()


def get_thread_session():
    """Get a thread-local database session."""
    engine = db.engine
    Session = scoped_session(sessionmaker(bind=engine))
    return Session


# Buffer to ensure text fits in PostgreSQL B-tree index (100 + 3 for "...")
SAFE_TEXT_LENGTH_BUFFER = 103
# Max length for text to fit in PostgreSQL B-tree index
SAFE_TEXT_LENGTH = 2000 - SAFE_TEXT_LENGTH_BUFFER
SLEEP_PER_REDDIT_REQUEST = (
    0.5  # Sleep time between chunks to avoid rate limits
)


def preprocess_text(text: str) -> str:
    """Clean and preprocess text content."""
    if not text:
        return ""
    # Encode and decode text in utf-8 format to remove unsupported characters
    cleaned_text = text.encode("utf-8", errors="ignore").decode("utf-8")
    # Remove hyperlinks
    cleaned_text = re.sub(r"\[.*?\]\((.*?)\)", r"\1", cleaned_text).strip()
    cleaned_text = re.sub(r'(https?:\/\/\S+|www\.\S+)', '', cleaned_text)

    # Truncate if too long to fit in PostgreSQL B-tree index
    encoded = cleaned_text.encode('utf-8')
    if len(encoded) > SAFE_TEXT_LENGTH:
        truncated = encoded[:SAFE_TEXT_LENGTH]
        # Find the last complete UTF-8 character
        while truncated and (truncated[-1] & 0xC0) == 0x80:
            truncated = truncated[:-1]
        cleaned_text = truncated.decode('utf-8', errors='ignore') + "..."
    return cleaned_text


def create_reddit_client() -> praw.Reddit:
    """Create and return a Reddit API client."""
    client = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        redirect_uri=Config.SQLALCHEMY_DATABASE_URI,
        user_agent=REDDIT_USER_AGENT,
    )
    time.sleep(
        SLEEP_PER_REDDIT_REQUEST,
    )  # Sleep to avoid hitting API rate limits immediately
    return client


def process_submission(
    submission,
    currency: CryptoAsset,
    subreddit: str,
    source_id: int,
    timestamp: datetime,
) -> CryptoRedditData:
    """Process a single Reddit submission and return data object."""
    title = preprocess_text(submission.title)
    body = preprocess_text(submission.selftext)

    # Check if submission already seen (thread-safe)
    with submission_set_lock:
        if title in submission_set:
            return None
        submission_set.add(title)

    return CryptoRedditData(
        symbol=currency.symbol,
        text=f"{title}\n{body}",
        subreddit=subreddit,
        source_id=source_id,
        votes=submission.score,
        confidence=1,
        timestamp=timestamp,
    )


def determine_comment_currency(
    comment_text: str,
    original_currency: CryptoAsset,
    all_currencies: List[CryptoAsset],
) -> tuple[str, float]:
    """Determine which currency a comment refers to and confidence level."""
    lowercase_text = comment_text.lower()

    # Check if comment references other cryptocurrencies
    for referenced_coin in all_currencies:
        if (
            referenced_coin.symbol.lower() in lowercase_text
            or referenced_coin.name.lower() in lowercase_text
        ):
            return referenced_coin.symbol, 1.0

    # Set weak confidence if no direct mention of original currency
    if (
        original_currency.symbol.lower() not in lowercase_text
        and original_currency.name.lower() not in lowercase_text
    ):
        return original_currency.symbol, 0.5

    return original_currency.symbol, 0.0


def process_comment(
    comment,
    currency: CryptoAsset,
    subreddit: str,
    source_id: int,
    timestamp: datetime,
    all_currencies: List[CryptoAsset],
) -> CryptoRedditData:
    """Process a single Reddit comment and return data object."""
    text = preprocess_text(comment.body)
    symbol, confidence = determine_comment_currency(
        text,
        currency,
        all_currencies,
    )

    return CryptoRedditData(
        symbol=symbol,
        text=text,
        subreddit=subreddit,
        source_id=source_id,
        votes=comment.score,
        confidence=confidence,
        timestamp=timestamp,
    )


def fetch_submissions_for_search_term(
    reddit,
    search_term: str,
    subreddit: str,
    time_range: str,
    limit: int = 10,
):
    """Fetch submissions for a specific search term."""
    try:
        return list(
            reddit.subreddit(subreddit).search(
                query=search_term,
                time_filter=time_range,
                limit=limit,
            ),
        )
    except Exception as e:
        logger.error(
            f"Error searching for '{search_term}' in {subreddit}: {e}",
        )
        return []


def process_submission_comments(
    submission,
    currency: CryptoAsset,
    subreddit: str,
    source_id: int,
    timestamp: datetime,
    all_currencies: List[CryptoAsset],
    max_comments: int = 20,
) -> List[CryptoRedditData]:
    """Process comments from a submission and return list of data objects."""
    comment_data = []

    try:
        # Limit comment processing for performance
        submission.comments.replace_more(
            limit=0,
        )  # Don't expand "more comments"
        comments = submission.comments.list()[
            :max_comments
        ]  # Limit to top comments

        for comment in comments:
            try:
                comment_obj = process_comment(
                    comment,
                    currency,
                    subreddit,
                    source_id,
                    timestamp,
                    all_currencies,
                )
                comment_data.append(comment_obj)
            except Exception as e:
                logger.warning(f"Error processing comment: {e}")
                continue

    except Exception as e:
        logger.error(f"Error processing comments for submission: {e}")

    return comment_data


def fetch_reddit_data_for_search_term(
    reddit,
    search_term: str,
    currency: CryptoAsset,
    subreddit: str,
    time_range: str,
    all_currencies: List[CryptoAsset],
    source_id: int,
    timestamp: datetime,
) -> List[CryptoRedditData]:
    """Fetch Reddit data for a single search term."""
    data = []

    submissions = fetch_submissions_for_search_term(
        reddit,
        search_term,
        subreddit,
        time_range,
    )

    for submission in submissions:
        try:
            # Process submission
            submission_data = process_submission(
                submission,
                currency,
                subreddit,
                source_id,
                timestamp,
            )
            if submission_data:
                data.append(submission_data)

            # Process comments
            comment_data = process_submission_comments(
                submission,
                currency,
                subreddit,
                source_id,
                timestamp,
                all_currencies,
            )
            data.extend(comment_data)

        except Exception as e:
            logger.error(f"Error processing submission: {e}")
            continue

    return data


def fetch_reddit_data_for_currency(
    currency: CryptoAsset,
    subreddit: str,
    time_range: str,
    all_currencies: List[CryptoAsset],
    timestamp: datetime,
    source_id: int,
) -> List[CryptoRedditData]:
    """Fetch Reddit data for a specific cryptocurrency and subreddit."""
    reddit = create_reddit_client()
    data = []

    # Search for both symbol and name
    search_terms = [currency.symbol, currency.name]

    for search_term in search_terms:
        try:
            term_data = fetch_reddit_data_for_search_term(
                reddit,
                search_term,
                currency,
                subreddit,
                time_range,
                all_currencies,
                source_id,
                timestamp,
            )
            data.extend(term_data)

        except Exception as e:
            logger.error(
                f"Error fetching Reddit data for {currency.symbol} "
                f"with term '{search_term}': {e}",
            )

    return data


def cleanup_session_safely(session, operation_name: str = "cleanup"):
    """Safely clean up database session with proper error handling."""
    cleanup_operations = [
        ('rollback', lambda: session.rollback()),
        ('close', lambda: session.close()),
        ('remove', lambda: session.remove()),
    ]

    for op_name, operation in cleanup_operations:
        try:
            operation()
        except Exception as e:
            logger.warning(f"Error during {op_name} in {operation_name}: {e}")


def execute_bulk_insert(session, batch_data: List[dict]) -> None:
    """Execute bulk insert with conflict resolution."""
    stmt = insert(CryptoRedditData)
    stmt = stmt.on_conflict_do_nothing(
        index_elements=['symbol', 'subreddit', 'text'],
    )
    session.execute(stmt, batch_data)


def process_batch_with_retry(
    session,
    batch: List[CryptoRedditData],
    batch_num: int,
    total_batches: int,
    max_retries: int = 3,
):
    """Process a single batch with retry logic."""
    retry_count = 0

    while retry_count < max_retries:
        try:
            logger.info(
                f"Processing batch {batch_num}/{total_batches} "
                f"({len(batch)} items)",
            )

            with session.begin():
                batch_data = [model_to_dict(data) for data in batch]
                execute_bulk_insert(session, batch_data)

            logger.info(f"Batch {batch_num}/{total_batches} completed")
            return True

        except OperationalError as e:
            retry_count += 1
            logger.warning(
                f"Database connection error on batch {batch_num} "
                f"(attempt {retry_count}): {e}",
            )

            if retry_count < max_retries:
                wait_time = 2**retry_count
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

                # Clean up and get fresh session
                cleanup_session_safely(session, f"batch {batch_num} retry")
                session = get_thread_session()
            else:
                logger.error(
                    f"Failed to store batch {batch_num} after "
                    f"{max_retries} attempts",
                )
                raise

        except Exception as e:
            logger.error(f"Unexpected error in batch {batch_num}: {e}")
            cleanup_session_safely(session, f"batch {batch_num} error")
            raise

    return False


def store_reddit_data(
    reddit_data: List[CryptoRedditData],
    batch_size: int = 1000,
):
    """Store Reddit data with optimised bulk operations."""
    if not reddit_data:
        return

    logger.info(
        f"Storing {len(reddit_data)} Reddit data points "
        f"in batches of {batch_size}",
    )

    session = get_thread_session()

    try:
        total_batches = (len(reddit_data) + batch_size - 1) // batch_size

        for i in range(0, len(reddit_data), batch_size):
            batch = reddit_data[i : i + batch_size]
            batch_num = (i // batch_size) + 1

            success = process_batch_with_retry(
                session,
                batch,
                batch_num,
                total_batches,
            )

            if not success:
                break

        logger.info(
            f"Successfully stored all {len(reddit_data)} Reddit data points",
        )

    finally:
        cleanup_session_safely(session, "final cleanup")


def create_work_items(
    cryptocurrencies: List[CryptoAsset],
    subreddits: List[str],
    time_range: str,
    source_id: int,
    timestamp: datetime,
) -> List[tuple]:
    """Create work items for concurrent processing."""
    return [
        (
            currency,
            subreddit,
            time_range,
            cryptocurrencies,
            timestamp,
            source_id,
        )
        for currency in cryptocurrencies
        for subreddit in subreddits
    ]


def process_chunk_concurrently(
    chunk_items: List[tuple],
    max_workers: int,
) -> List[CryptoRedditData]:
    """Process a chunk of work items concurrently."""
    chunk_data = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_work = {}

        for work_item in chunk_items:
            (
                currency,
                subreddit,
                time_range,
                cryptocurrencies,
                timestamp,
                source_id,
            ) = work_item

            future = executor.submit(
                fetch_reddit_data_for_currency,
                currency,
                subreddit,
                time_range,
                cryptocurrencies,
                timestamp,
                source_id,
            )
            future_to_work[future] = work_item

        for future in as_completed(future_to_work):
            work_item = future_to_work[future]
            currency, subreddit = work_item[0], work_item[1]

            try:
                data = future.result()
                if data:
                    chunk_data.extend(data)
                    logger.info(
                        f"Fetched {len(data)} items for "
                        f"{currency.symbol} from {subreddit}",
                    )
            except Exception as e:
                logger.error(
                    f"Error processing {currency.symbol} "
                    f"from {subreddit}: {e}",
                )

    return chunk_data


def get_cryptocurrencies_and_source():
    """Get cryptocurrencies and Reddit source from database."""
    query = (
        select(CryptoAsset)
        .distinct()
        .join(CryptoMarketData, CryptoAsset.symbol == CryptoMarketData.symbol)
        .order_by(CryptoAsset.ranking)
        .limit(TOP_CRYPTOCURRENCIES_LIMIT)
    )
    cryptocurrencies = db.session.execute(query).scalars().all()

    source = CryptoSource.query.filter(CryptoSource.name == "reddit").first()
    if not source:
        raise ValueError("Reddit source not found in CryptoSource table.")

    return cryptocurrencies, source.id


def fetch_reddit_data_concurrent(
    subreddits: List[str],
    time_range: str = "hour",
    max_workers: int = 10,
):
    """Fetch Reddit data for multiple cryptocurrencies concurrently."""
    # Clear submission set for new fetch
    global submission_set
    with submission_set_lock:
        submission_set.clear()

    try:
        cryptocurrencies, source_id = get_cryptocurrencies_and_source()
    except ValueError as e:
        logger.error(str(e))
        return

    timestamp = datetime.now(timezone.utc)

    work_items = create_work_items(
        cryptocurrencies,
        subreddits,
        time_range,
        source_id,
        timestamp,
    )

    all_data = []
    chunk_size = 20

    for chunk_start in range(0, len(work_items), chunk_size):
        chunk_items = work_items[chunk_start : chunk_start + chunk_size]

        logger.info(
            f"Processing chunk {chunk_start//chunk_size + 1}/"
            f"{(len(work_items) + chunk_size - 1)//chunk_size}",
        )

        chunk_data = process_chunk_concurrently(chunk_items, max_workers)

        # Store chunk data immediately
        if chunk_data:
            try:
                store_reddit_data(chunk_data)
                all_data.extend(chunk_data)
            except Exception as e:
                logger.error(f"Failed to store chunk data: {e}")

    logger.info(f"Reddit data fetch completed. Total items: {len(all_data)}")


def cleanup_database_connections():
    """Clean up database connections safely."""
    cleanup_operations = [
        ('close session', lambda: db.session.close()),
        ('remove session', lambda: db.session.remove()),
        (
            'remove scoped session',
            lambda: (
                db.session.remove()
                if hasattr(db, 'session')
                and isinstance(db.session, scoped_session)
                else None
            ),
        ),
    ]

    for operation_name, operation in cleanup_operations:
        try:
            result = operation()
            if result is None and operation_name == 'remove scoped session':
                continue  # Skip logging for None result
        except Exception as e:
            logger.warning(f"Error during {operation_name}: {e}")


def collect_reddit_crypto_discussions(
    subreddits: List[str],
    time_range: str = "hour",
    max_workers: int = 10,
):
    """Main entry point for Reddit data fetching task."""
    try:
        fetch_reddit_data_concurrent(subreddits, time_range, max_workers)
    finally:
        cleanup_database_connections()
