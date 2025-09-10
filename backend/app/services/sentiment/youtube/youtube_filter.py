from dataclasses import dataclass
from functools import partial
import re
from collections import Counter
from typing import Generator, Iterable, List, Tuple
from langdetect import detect, LangDetectException
from emoji import emoji_count
from sqlalchemy import select

from app.extensions import db
from app.models.crypto import CryptoAsset, CryptoMarketData
from app.schemas.youtube_schema import YoutubeCommentInfo
from app.utils.decorators import transactional

import logging

from app.utils import compose_filters

logger = logging.getLogger(__name__)


@dataclass
class CryptoAssetPattern:
    symbol: str
    pattern: re.Pattern[str]


SPAM_PATTERNS = [
    r'(?i)\b(subscribe|like|follow)\b.*\b(back|sub4sub|f4f)\b',
    r'(?i)\b(check.*out|visit).*\b(channel|profile|link)\b',
    r'(?i)\b(make.*money|earn.*\$|click.*here|amazing.*opportunity)\b',
    r'(?i)\b(bot|automated|script)\b',
    r'^\s*[!@#$%^&*()_+=\[\]{}|;:,.<>?]*\s*$',  # Only special characters
    r'(?i)\b(first|early|notification.*squad)\b',
    r'https?://\S+',  # URLs,
    r'(?i)\b(visit|click|check).*?\b(link|website|profile)\b',
    r'(?i)\bsubscribe\b.*\bchannel\b',
]

CRYPTO_ASSET_MATCHING_PATTERN = r"\b({}|{})((['’]s)?s?)\b[.,!?;:]*"


def create_comment_fingerprint(text: str) -> str:
    """Create a normalized fingerprint of the comment."""
    # Remove special chars, convert to lowercase, remove extra spaces
    normalized = re.sub(r'[^\w\s]', '', text.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    # Sort words to catch reordered spam
    words = sorted(normalized.split())
    return ' '.join(words)


def check_spam_patterns(text: str) -> float:
    """Check for known spam patterns."""
    matches = sum(1 for pattern in SPAM_PATTERNS if re.search(pattern, text))
    return min(matches * 0.3, 0.8)  # Cap at 0.8


@transactional
def get_crypto_asset_patterns(ranking: int) -> List[CryptoAssetPattern]:
    """
    Get crypto asset patterns from the database.

    Pattern: `\\b(symbol|name)(['’]s)?s?\\b`
    - This will match: `BTC`, `BTC's`, `BTCs`, `BTC!`, `Bitcoin's!`
    """
    crypto_assets = (
        db.session.execute(
            select(CryptoAsset)
            .distinct()
            .join(
                CryptoMarketData,
                CryptoAsset.symbol == CryptoMarketData.symbol,
            )
            .order_by(CryptoAsset.ranking)
            .limit(ranking),
        )
        .scalars()
        .all()
    )

    patterns = []
    if not crypto_assets:
        logger.warning(
            "No crypto assets found in the database. "
            "Skipping crypto comment filtering.",
        )
        return patterns

    for asset in crypto_assets:
        pattern = re.compile(
            CRYPTO_ASSET_MATCHING_PATTERN.format(
                re.escape(asset.symbol),
                re.escape(asset.name),
            ),
            re.IGNORECASE,
        )
        patterns.append(
            CryptoAssetPattern(symbol=asset.symbol, pattern=pattern),
        )

    return patterns


def check_comment_characteristics(comment: YoutubeCommentInfo) -> float:
    """Check comment characteristics that indicate bots."""
    text = comment.text
    score = 0.0

    # Very short comments
    if len(text.strip()) < 10:
        score += 0.2

    # Too many emojis
    if emoji_count(text) > len(text.split()) * 0.5:
        score += 0.3

    # All caps
    if text.isupper() and len(text) > 10:
        score += 0.2

    # Excessive punctuation
    punct_ratio = len(re.findall(r'[!?]{2,}', text)) / max(len(text), 1)
    if punct_ratio > 0.1:
        score += 0.2

    # No actual words (just numbers/symbols)
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
    if len(words) < 2 and len(text) > 5:
        score += 0.4

    return min(score, 0.8)


def check_author_patterns(author: str) -> float:
    """Check author name patterns that indicate bots."""
    score = 0.0

    # Random character patterns
    if re.match(r'^[a-zA-Z]+\d{4,}$', author):  # Name followed by many digits
        score += 0.3

    # Generic names
    generic_patterns = [
        r'(?i)^(user|guest|member|visitor)\d+',
        r'(?i)^[a-z]{6,12}\d{2,4}$',  # Random letters + numbers
    ]

    for pattern in generic_patterns:
        if re.match(pattern, author):
            score += 0.2
            break

    return min(score, 0.5)


def is_bot_comment(comment: YoutubeCommentInfo) -> Tuple[bool, float]:
    """
    Detect if a comment is likely from a bot.
    Returns (is_bot, bot_score)
    """
    reasons = []

    # Check for spam patterns
    spam_score = check_spam_patterns(comment.text)

    # Check comment characteristics
    char_score = check_comment_characteristics(comment)

    # Check author patterns
    author_score = check_author_patterns(comment.author)

    # Calculate total score
    total_score = spam_score + char_score + author_score

    # Add reasons for debugging
    if spam_score > 0:
        reasons.append(f"spam({spam_score:.2f})")
    if char_score > 0:
        reasons.append(f"chars({char_score:.2f})")
    if author_score > 0:
        reasons.append(f"author({author_score:.2f})")

    # Normalize score (max possible is ~1.5)
    final_score = min(total_score / 1.5, 1.0)
    is_bot = final_score > 0.5

    return is_bot, final_score


def is_english_comment(comment: YoutubeCommentInfo) -> bool:
    """
    Check if a comment is in English using multiple methods.
    """
    text = comment.text.strip()

    # Skip very short comments or emoji-only comments
    if len(text) < 3:
        return True  # Give benefit of doubt for very short comments

    try:
        detected_lang = detect(text)
        if detected_lang == 'en':
            return True
        return False
    except LangDetectException:
        logger.warning(f"LangDetect failed for comment: '{text[:50]}...'")
        pass

    return False


def exclude_bot_comments(
    comments: Iterable[YoutubeCommentInfo],
) -> Generator[YoutubeCommentInfo, None, None]:
    """Filter out only bot comments, keep duplicates and all languages."""
    filtered_comment_count = 0
    for comment in comments:
        is_bot, bot_score = is_bot_comment(comment)
        if not is_bot:
            comment.bot_score = bot_score
            yield comment
        else:
            filtered_comment_count += 1
    logger.info(f"🤖 Filtered out {filtered_comment_count} bot comments.")


def filter_english_comments(
    comments: Iterable[YoutubeCommentInfo],
) -> Generator[YoutubeCommentInfo, None, None]:
    """Filter out only non-English comments, keep bots and duplicates."""
    filtered_comment_count = 0
    for comment in comments:
        if is_english_comment(comment):
            yield comment
        else:
            filtered_comment_count += 1
    logger.info(
        f"🌎 Filtered out {filtered_comment_count} non-English comments.",
    )


def filter_unique_comments(
    comments: Iterable[YoutubeCommentInfo],
) -> Generator[YoutubeCommentInfo, None, None]:
    """
    Yield only comments that are not duplicated anywhere else (appear exactly once).
    Logs the number of filtered duplicate comments.
    """
    comments = list(comments)
    fingerprints = [create_comment_fingerprint(c.text) for c in comments]
    counts = Counter(fingerprints)
    filtered_comment_count = 0
    for comment in comments:
        fingerprint = create_comment_fingerprint(comment.text)
        if counts[fingerprint] == 1:
            yield comment
        else:
            filtered_comment_count += 1
    logger.info(f"🔁 Filtered out {filtered_comment_count} duplicate comments.")


def filter_crypto_comments(
    comments: Iterable[YoutubeCommentInfo],
    ranking: int,
) -> Generator[YoutubeCommentInfo, None, None]:
    """
    Filter out comments that do not mention any crypto assets.
    This is a placeholder function for future implementation.
    """
    asset_patterns = get_crypto_asset_patterns(ranking)
    if not asset_patterns:
        logger.warning(
            "No crypto assets found in the database."
            " Skipping crypto comment filtering.",
        )
        yield from ()
    filtered_comment_count = 0

    for comment in comments:
        for asset in asset_patterns:
            if asset.pattern.search(comment.text):
                comment.crypto_mentions.append(asset.symbol)
                yield comment
                break
        else:
            filtered_comment_count += 1

    logger.info(
        f"₿ Filtered out {filtered_comment_count} comments without crypto mention.",
    )


def sanitise_comments(
    comments: Iterable[YoutubeCommentInfo],
    ranking: int,
) -> List[YoutubeCommentInfo]:
    """
    Sanitise comments using the defined pipeline:
    - Filter out bot comments
    - Filter out non-English comments
    - Filter out all duplicates (keep only unique comments)
    - Filter out comments without mention of crypto assets
    """
    comment_filter_pipeline = compose_filters(
        exclude_bot_comments,
        filter_english_comments,
        filter_unique_comments,
        partial(filter_crypto_comments, ranking=ranking),
    )
    return list(comment_filter_pipeline(comments))
