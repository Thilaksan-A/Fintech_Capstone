from datetime import datetime
from app.models import YoutubeCommentAnalysis
from tests.factories.youtube import (
    YoutubeCommentAnalysisFactory,
    YoutubeCommentFactory,
    CryptoAssetFactory,
)


def test_youtube_comment_analysis(session):
    # Create with custom values
    comment = YoutubeCommentFactory(
        comment_id="custom_comment_123",
        text_original="Bitcoin is going to the moon! 🚀",
    )

    crypto_asset = CryptoAssetFactory(symbol="BTC", name="Bitcoin")

    analysis = YoutubeCommentAnalysisFactory(
        comment=comment,
        crypto_asset=crypto_asset,
        confidence_score=0.95,
        relevance_score=0.88,
        quality_score=0.92,
        analysed_at=datetime(2025, 7, 17, 10, 30, 0).astimezone(),
    )

    # Test custom values
    assert analysis.comment_id == "custom_comment_123"
    assert analysis.crypto_symbol == "BTC"
    assert analysis.confidence_score == 0.95
    assert analysis.relevance_score == 0.88
    assert analysis.quality_score == 0.92
    assert analysis.analysed_at.year == 2025
    assert analysis.analysed_at.month == 7
    assert analysis.analysed_at.day == 17

    # Test relationships
    assert analysis.comment.text_original == "Bitcoin is going to the moon! 🚀"
    assert analysis.crypto_asset.name == "Bitcoin"


def test_youtube_comment_analysis_database_persistence(session):
    # Create and save analysis
    analysis = YoutubeCommentAnalysisFactory()

    # Retrieve from database
    retrieved = (
        session.query(YoutubeCommentAnalysis)
        .filter_by(
            comment_id=analysis.comment_id,
            crypto_symbol=analysis.crypto_symbol,
        )
        .first()
    )

    assert retrieved is not None
    assert retrieved.confidence_score == analysis.confidence_score
    assert retrieved.relevance_score == analysis.relevance_score
    assert retrieved.quality_score == analysis.quality_score
    assert retrieved.comment.comment_id == analysis.comment_id
    assert retrieved.crypto_asset.symbol == analysis.crypto_symbol


def test_youtube_comment_multiple_analyses(session):
    comment = YoutubeCommentFactory(
        text_original="Both Bitcoin and Ethereum are looking bullish",
    )

    btc_asset = CryptoAssetFactory(symbol="BTC", name="Bitcoin")
    eth_asset = CryptoAssetFactory(symbol="ETH", name="Ethereum")

    btc_analysis = YoutubeCommentAnalysisFactory(
        comment=comment,
        crypto_asset=btc_asset,
        confidence_score=0.85,
    )

    eth_analysis = YoutubeCommentAnalysisFactory(
        comment=comment,
        crypto_asset=eth_asset,
        confidence_score=0.78,
    )

    # Test that both analyses exist
    assert len(comment.analysis) == 2
    assert btc_analysis in comment.analysis
    assert eth_analysis in comment.analysis

    # Test that analyses have correct crypto assets
    crypto_symbols = [analysis.crypto_symbol for analysis in comment.analysis]
    assert "BTC" in crypto_symbols
    assert "ETH" in crypto_symbols
