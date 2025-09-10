import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
from app.models import (
    CryptoRedditData,
    CryptoCoingeckoSentimentData,
    CryptoSentimentAggregateData,
    CryptoNewsData,
    YoutubeComment,
    YoutubeCommentAnalysis,
    CryptoMarketData,
)
from app.extensions import db
from app.utils.decorators import transactional
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import select
from dataclasses import dataclass
from app.constants import TOP_CRYPTOCURRENCIES_LIMIT


nltk.download('punkt_tab')
logger = logging.getLogger(__name__)


@dataclass
class SocialDataPoint:
    symbol: str
    text: str
    confidence: float


def process_crypto_sentiment_analysis(days_to_fetch: int = 2):
    """
    Main entry point for the sentiment analysis task.
    This function is used in cron jobs to analyze and store sentiment data.
    """
    logger.info("Starting sentiment analysis task.")
    analyse_and_store_sentiment(days_to_fetch)
    logger.info("Sentiment analysis task completed.")


@transactional
def analyse_and_store_sentiment(days_to_fetch):
    """Main function to analyze and store sentiment data."""
    # Set time range
    earliest = datetime.today() - timedelta(days=days_to_fetch)

    coingecko_data, social_data = fetch_sentiment_data(earliest)
    processed_data = analyse_sentiment_data(
        coingecko_data,
        social_data,
        earliest,
    )

    # Write data directly - transaction handled by decorator
    logger.info("Writing aggregated sentiment data to database")
    for rec in processed_data:
        db.session.merge(rec)

    logger.info(
        f"Successfully wrote {len(processed_data)} records to database.",
    )


@transactional
def fetch_sentiment_data(
    earliest,
) -> tuple[list[CryptoCoingeckoSentimentData], list[SocialDataPoint]]:
    """Fetch data from various sources for sentiment analysis."""
    logger.info("Retrieving social data for analysis...")

    # Fetch the latest set of coingecko aggregate data for the top 50 cryptocurrencies
    query = (
        select(CryptoCoingeckoSentimentData)
        .distinct(CryptoCoingeckoSentimentData.symbol)
        .join(
            CryptoMarketData,
            CryptoCoingeckoSentimentData.symbol == CryptoMarketData.symbol,
        )
        .order_by(
            CryptoCoingeckoSentimentData.symbol.desc(),
            CryptoCoingeckoSentimentData.timestamp.desc(),
        )
        .limit(TOP_CRYPTOCURRENCIES_LIMIT)
    )
    coingecko_data = db.session.execute(query).scalars().all()

    # Fetch recent social data for cryptocurrencies
    reddit_data = CryptoRedditData.query.filter(
        CryptoRedditData.timestamp >= earliest,
    ).all()
    news_data = CryptoNewsData.query.filter(
        CryptoNewsData.timestamp >= earliest,
    ).all()

    youtube_stmt = (
        select(YoutubeComment, YoutubeCommentAnalysis)
        .join(
            YoutubeCommentAnalysis,
            YoutubeComment.comment_id == YoutubeCommentAnalysis.comment_id,
        )
        .where(YoutubeComment.published_at >= earliest)
    )
    youtube_raw = db.session.execute(youtube_stmt).all()

    # Extract data into new data transfer object
    social_data = []

    # Process YouTube data
    for comment, analysis in youtube_raw:
        aggregated_confidence = (
            (analysis.confidence_score or 0)
            + (analysis.relevance_score or 0)
            + (analysis.quality_score or 0)
        ) / 3
        social_data.append(
            SocialDataPoint(
                symbol=analysis.crypto_symbol,
                text=comment.text_original,
                confidence=aggregated_confidence,
            ),
        )

    # Process Reddit data
    for comment in reddit_data:
        social_data.append(
            SocialDataPoint(
                symbol=comment.symbol,
                text=comment.text,
                confidence=comment.confidence,
            ),
        )

    # Process News data
    for article in news_data:
        social_data.append(
            SocialDataPoint(
                symbol=article.symbol,
                text=article.title + article.description,
                confidence=1.0,
            ),
        )

    logger.info("Data successfully retrieved.")
    return (coingecko_data, social_data)


def analyse_sentiment_data(
    coingecko,
    social_data,
    earliest,
) -> list[CryptoSentimentAggregateData]:
    """
    Analyses and normalise all sentiment data from various social sources.
    Returns result in the form of CryptoSentimentAggregatedata database objects.
    """
    logger.info("Analysing social data with Vader Sentiment Analysis Tool.")

    # Map of all sentiment data for each of the top cryptocurrencies
    currency_map = dict()
    analyser = SentimentIntensityAnalyzer()

    # Process Coingecko data
    for data in coingecko:
        rec = currency_map.setdefault(data.symbol, defaultdict(float))
        rec["sentiment_up_percentage"] = data.sentiment_up_percentage
        rec["sentiment_down_percentage"] = data.sentiment_down_percentage

    # Process social media data
    for data in social_data:
        rec = currency_map.setdefault(data.symbol, defaultdict(float))
        sentiment_dict = analyser.polarity_scores(data.text)
        confidence = data.confidence

        rec["avg_positive_sentiment"] += sentiment_dict['pos'] * confidence
        rec["avg_neutral_sentiment"] += sentiment_dict['neu'] * confidence
        rec["avg_negative_sentiment"] += sentiment_dict['neg'] * confidence
        rec["avg_compound_score"] += sentiment_dict['compound'] * confidence
        rec["total_weight"] += confidence

        # Add 'weighted' counts for positive, negative and neutral sentiment based on
        # assigned confidence
        if sentiment_dict['compound'] >= 0.05:
            rec["positive_count"] += confidence
        elif sentiment_dict['compound'] <= -0.05:
            rec["negative_count"] += confidence
        else:
            rec["neutral_count"] += confidence

    # Get average sentiment from all data points
    processed_data = []
    for key in currency_map:
        currency = currency_map[key]
        if currency["total_weight"] != 0:
            currency["avg_positive_sentiment"] /= currency["total_weight"]
            currency["avg_neutral_sentiment"] /= currency["total_weight"]
            currency["avg_negative_sentiment"] /= currency["total_weight"]
            currency["avg_compound_score"] /= currency["total_weight"]

        combined_sentiment = apply_laplace_smoothing(
            currency['positive_count'],
            currency['negative_count'],
            currency["sentiment_up_percentage"],
            currency["sentiment_down_percentage"],
        )

        processed_data.append(
            CryptoSentimentAggregateData(
                symbol=key,
                normalised_up_percentage=combined_sentiment['pos_pct'],
                normalised_down_percentage=combined_sentiment['neg_pct'],
                avg_positive_sentiment=currency['avg_positive_sentiment'],
                avg_neutral_sentiment=currency['avg_neutral_sentiment'],
                avg_negative_sentiment=currency['avg_negative_sentiment'],
                avg_compound_sentiment=currency['avg_compound_score'],
                earliest_post=earliest,
            ),
        )

        logger.debug(key)
        logger.debug(
            " Negative Sentiment: %s",
            currency['avg_negative_sentiment'],
        )
        logger.debug(
            " Neutral Sentiment: %s",
            currency['avg_neutral_sentiment'],
        )
        logger.debug(
            " Positive Sentiment: %s",
            currency['avg_positive_sentiment'],
        )
        logger.debug(
            " Compound Sentiment: %s",
            currency['avg_compound_score'],
        )
        logger.debug(
            " positive_count: %s",
            currency['positive_count'],
        )
        logger.debug(
            " negative_count: %s",
            currency['negative_count'],
        )
        logger.debug(
            " neutral_count: %s",
            currency['neutral_count'],
        )
        logger.debug(
            " Original Up %%: %s",
            currency['sentiment_up_percentage'],
        )
        logger.debug(
            " Normalised Up %%: %s",
            combined_sentiment['pos_pct'],
        )
        logger.debug(
            " Normalised Down %%: %s",
            combined_sentiment['neg_pct'],
        )

    logger.info(
        "Successfully analysed %d data points.",
        len(social_data),
    )
    return processed_data


def apply_laplace_smoothing(
    positive_count: float,
    negative_count: float,
    sentiment_up_percentage: float,
    sentiment_down_percentage: float,
) -> dict[str, float]:
    """
    Apply Laplace Smoothing if dataset is below threshold to prevent extreme
    sentiment shifts when reconciling with Coingecko sentiment data.
    Higher alpha moves value towards uniform (0.5).

    Reference:
    https://towardsdatascience.com/laplace-smoothing-in-naive-bayes-algorithm-9c237a8bdece/

    Returns:
        Dict with smoothed positive percentage as 'pos_pct' and negative
        percentage as 'neg_pct'.
    """
    alpha = 2.0
    k = 2.0
    min_post = 10
    total_count = positive_count + negative_count
    sentiment_up_percentage = (
        sentiment_up_percentage / 100 if sentiment_up_percentage else 0.5
    )
    sentiment_down_percentage = (
        sentiment_down_percentage / 100 if sentiment_down_percentage else 0.5
    )

    pos_pct = sentiment_up_percentage
    neg_pct = sentiment_down_percentage

    # Apply Laplace Smoothing if number of collected data points is too low
    if total_count > 0 and total_count < min_post:
        smoothed_pos_pct = (positive_count + alpha) / (total_count + k * alpha)
        smoothed_neg_pct = (negative_count + alpha) / (total_count + k * alpha)
        pos_pct = (sentiment_up_percentage + smoothed_pos_pct) / 2
        neg_pct = (sentiment_down_percentage + smoothed_neg_pct) / 2

    # Otherwise, return simple average of Vader sentiments and Coingecko sentiments
    elif total_count > 0:
        pos_pct = (sentiment_up_percentage + positive_count / total_count) / 2
        neg_pct = (
            sentiment_down_percentage + negative_count / total_count
        ) / 2

    return {
        "pos_pct": pos_pct,
        "neg_pct": neg_pct,
    }


def tokenise_sentences(sentence) -> str:
    """Tokenize sentence into multiple sentences using NLTK."""
    split_sentences = nltk.tokenize.sent_tokenize(sentence, language='english')
    return split_sentences
