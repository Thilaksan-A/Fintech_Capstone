from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import desc, func, select, and_
from app.extensions import db
from app.services.forecast.gemini_client import ask_gemini
from app.models.user import UserProfile
from app.models.crypto import (
    CryptoTechnicalIndicator,
    CryptoAsset,
    CryptoMarketData,
    CryptoSentimentAggregateData,
)
from app.schemas.crypto_schema import CryptoAssetSchema
from datetime import timedelta, datetime
from app.utils.decorators import retry_request
from app.env import NEWS_API_KEY_FRONTEND
import requests

crypto_bp = Blueprint('crypto', __name__)


@crypto_bp.route("/latest_indicators", methods=["GET"])
@retry_request
def get_latest_indicators():
    symbol = request.args.get("symbol", "").upper()

    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    stmt = (
        select(CryptoTechnicalIndicator)
        .where(CryptoTechnicalIndicator.symbol == symbol)
        .where(CryptoTechnicalIndicator.interval == "1h")
        .order_by(desc(CryptoTechnicalIndicator.timestamp))
        .limit(1)
    )

    result = db.session.execute(stmt).scalar_one_or_none()

    if not result:
        return (
            jsonify({"error": f"No technical indicators found for {symbol}"}),
            404,
        )

    return jsonify(
        {
            "symbol": result.symbol,
            "ema": float(result.ema),
            "rsi": float(result.rsi),
            "macd": float(result.macd),
        },
    )


@crypto_bp.route("/metadata", methods=["GET"])
@cross_origin(origins="http://localhost:5173")
@retry_request
def get_metadata():
    symbol = request.args.get("symbol", "").upper()

    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    stmt = select(CryptoAsset).where(CryptoAsset.symbol == symbol)

    result = db.session.execute(stmt).scalar_one_or_none()
    if not result:
        return jsonify({"error": f"No metadata found for {symbol}"}), 404

    return CryptoAssetSchema().jsonify(result)


top_rank_cache = dict()


@crypto_bp.route("/top_ranking", methods=["GET"])
@retry_request
def get_top_ranking(set_rankings=10):

    global top_rank_cache
    ranking = request.args.get("ranking", set_rankings, type=int)

    if ranking in top_rank_cache:
        rec = top_rank_cache[ranking]
        time_diff = (datetime.now() - rec[1]).total_seconds()
        # Check if news data is over 30 mins old and too stale
        if time_diff <= 600:
            return jsonify(rec[0]), 200

    print("Fetching fresh ranking data")

    try:
        # Create a subquery to get the latest price for each symbol
        latest_price_subquery = select(
            CryptoMarketData.symbol,
            CryptoMarketData.price.label('latest_price'),
            CryptoMarketData.ingested_at.label('latest_timestamp'),
            func.row_number()
            .over(
                partition_by=CryptoMarketData.symbol,
                order_by=CryptoMarketData.timestamp.desc(),
            )
            .label('rn'),
        ).subquery()

        # Filter to get only the latest price per symbol
        latest_prices = (
            select(
                latest_price_subquery.c.symbol,
                latest_price_subquery.c.latest_price,
                latest_price_subquery.c.latest_timestamp,
            ).where(latest_price_subquery.c.rn == 1)
        ).subquery()

        # Create a subquery to get 24h ago prices
        price_24h_subquery = (
            select(
                CryptoMarketData.symbol,
                CryptoMarketData.price.label('price_24h_ago'),
                CryptoMarketData.timestamp.label('timestamp_24h'),
                func.row_number()
                .over(
                    partition_by=CryptoMarketData.symbol,
                    order_by=func.abs(
                        func.extract('epoch', CryptoMarketData.timestamp)
                        - func.extract(
                            'epoch',
                            latest_prices.c.latest_timestamp
                            - timedelta(hours=24),
                        ),
                    ),
                )
                .label('rn'),
            )
            .join(
                latest_prices,
                CryptoMarketData.symbol == latest_prices.c.symbol,
            )
            .where(
                CryptoMarketData.timestamp
                >= latest_prices.c.latest_timestamp - timedelta(hours=25),
                CryptoMarketData.timestamp
                <= latest_prices.c.latest_timestamp - timedelta(hours=23),
            )
            .subquery()
        )

        # Filter to get the closest 24h ago price
        prices_24h = (
            select(
                price_24h_subquery.c.symbol,
                price_24h_subquery.c.price_24h_ago,
            ).where(price_24h_subquery.c.rn == 1)
        ).subquery()

        # Join everything together
        main_query = (
            select(
                CryptoAsset.symbol,
                CryptoAsset.name,
                CryptoAsset.image,
                CryptoAsset.ranking,
                latest_prices.c.latest_price,
                latest_prices.c.latest_timestamp,
                prices_24h.c.price_24h_ago,
            )
            .join(latest_prices, CryptoAsset.symbol == latest_prices.c.symbol)
            .outerjoin(prices_24h, CryptoAsset.symbol == prices_24h.c.symbol)
            .order_by(CryptoAsset.ranking)
            .limit(ranking)
        )

        results = db.session.execute(main_query).all()
        data = []

        for row in results:
            # Calculate price change percentage
            price_change_24h = None
            if (
                row.price_24h_ago
                and row.price_24h_ago > 0
                and row.latest_price
            ):
                price_change_24h = (
                    (row.latest_price - row.price_24h_ago) / row.price_24h_ago
                ) * 100

            data.append(
                {
                    "symbol": row.symbol,
                    "name": row.name,
                    "image": row.image,
                    "price": float(row.latest_price)
                    if row.latest_price
                    else 0,
                    "price_change_24h": round(price_change_24h, 2)
                    if price_change_24h is not None
                    else None,
                    "market_cap_rank": row.ranking,
                    "timestamp": row.latest_timestamp.isoformat()
                    if row.latest_timestamp
                    else None,
                },
            )

        top_rank_cache[ranking] = (data, datetime.now())

        return jsonify(data)

    except Exception as e:
        print(f"Database error in get_top_ranking: {str(e)}")
        db.session.rollback()
        return (
            jsonify({"error": "Database connection error. Please try again."}),
            500,
        )


@crypto_bp.route("/price_history", methods=["GET"])
@retry_request
def get_price_history():
    symbol = request.args.get("symbol", "").upper()
    interval = request.args.get("interval", "")

    if not symbol:
        return jsonify({"error": "Symbol parameter is required"}), 400

    # Get the latest timestamp for the given symbol
    latest_stmt = (
        select(CryptoMarketData.timestamp)
        .where(CryptoMarketData.symbol == symbol)
        .order_by(desc(CryptoMarketData.timestamp))
        .limit(1)
    )
    latest_result = db.session.execute(latest_stmt).scalar()
    print(f"Latest timestamp for {symbol}: {latest_result}")

    if not latest_result:
        return jsonify({"error": f"No price history found for {symbol}"}), 404

    # Always set end_dt to latest_result
    end_dt = latest_result
    if interval == '1D':
        start_dt = end_dt - timedelta(days=1)
    elif interval == '1M':
        start_dt = end_dt - timedelta(days=30)
    else:
        start_dt = None

    print(f"Fetching price history for {symbol} from {start_dt} to {end_dt}")
    sentiment_join_condition = and_(
        func.date_trunc('day', CryptoMarketData.timestamp)
        == func.date_trunc('day', CryptoSentimentAggregateData.timestamp),
        CryptoMarketData.symbol == CryptoSentimentAggregateData.symbol,
    )
    stmt = (
        select(
            CryptoMarketData.timestamp,
            CryptoMarketData.price,
            CryptoTechnicalIndicator.rsi,
            CryptoTechnicalIndicator.ema,
            CryptoTechnicalIndicator.macd,
            CryptoSentimentAggregateData.normalised_up_percentage,
        )
        .where(CryptoMarketData.symbol == symbol)
        .outerjoin(
            CryptoTechnicalIndicator,
            and_(
                CryptoMarketData.symbol == CryptoTechnicalIndicator.symbol,
                CryptoMarketData.timestamp
                == CryptoTechnicalIndicator.timestamp,
            ),
        )
        .outerjoin(CryptoSentimentAggregateData, sentiment_join_condition)
    )

    if start_dt:
        stmt = stmt.where(CryptoMarketData.timestamp >= start_dt)
    stmt = stmt.where(CryptoMarketData.timestamp <= end_dt)

    stmt = stmt.order_by(CryptoMarketData.timestamp)

    result = db.session.execute(stmt).fetchall()

    if not result:
        return jsonify({"error": f"No price history found for {symbol}"}), 404

    return jsonify(
        [
            {
                "timestamp": row.timestamp.isoformat(),
                "price": float(row.price),
                "rsi": float(row.rsi) if row.rsi else None,
                "ema": float(row.ema) if row.ema else None,
                "macd": float(row.macd) if row.macd else None,
                "sentiment": float(row.normalised_up_percentage * 100)
                if row.normalised_up_percentage
                else None,
            }
            for row in result
        ],
    )


@crypto_bp.route("/sentiment/all")
@retry_request
def get_all_sentiment():
    symbol = request.args.get('symbol')
    stmt = (
        select(CryptoSentimentAggregateData)
        .where(CryptoSentimentAggregateData.symbol == symbol.upper())
        .limit(1)
    )
    result = db.session.execute(stmt).scalar_one_or_none()

    return jsonify(
        {
            'normalised_up_percentage': result.normalised_up_percentage,
            'normalised_down_percentage': result.normalised_down_percentage,
        },
    )


@crypto_bp.route('/forecast', methods=["POST"])
@jwt_required()
def forecast_trades():
    data = request.get_json() or {}
    symbol = data.get('symbol', '').upper()
    if not symbol:
        return jsonify(error="Symbol is missing"), 400

    user_id = get_jwt_identity()
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile or not profile.investor_type:
        return jsonify(error="User profile is incomplete"), 400
    inv_type = profile.investor_type

    indicators = data.get("indicators")
    if not isinstance(indicators, dict):
        tech_indicators = CryptoTechnicalIndicator.get_recent_by_symbol(symbol)
        indicators = {
            "rsi": float(tech_indicators.rsi),
            "macd": float(tech_indicators.macd),
            "ema": float(tech_indicators.ema),
            "sentiment": CryptoSentimentAggregateData.get_latest_sentiment_score(
                symbol,
            ),
        }

    try:
        result = ask_gemini(inv_type, symbol, indicators)
    except Exception as e:
        return jsonify(error=str(e)), 502

    return (
        jsonify(
            {
                "symbol": symbol,
                "investor_type": inv_type.value,
                "indicators": indicators,
                **result,
            },
        ),
        200,
    )


news_cache = dict()


@crypto_bp.route('/news', methods=["GET"])
def get_news():
    global news_cache

    query = request.args.get('query', 'cryptocurrency').lower()
    refresh = request.args.get('refresh', 'false').lower()
    if not query:
        return jsonify(error="Query is missing"), 400

    if query in news_cache and refresh != "true":
        rec = news_cache[query]
        time_diff = (datetime.now() - rec[1]).total_seconds()
        # Check if news data is over an hour old and too stale
        if time_diff <= 3600:
            return jsonify(rec[0]), 200

    print("Fetching fresh news data")

    date_range = datetime.now() - timedelta(days=2)
    date = date_range.strftime("%Y-%m-%d")

    res = requests.get(
        f"https://newsapi.org/v2/everything?q={query}&from={date}&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY_FRONTEND}",
    )
    data = res.json()["articles"]
    # Update the time the news data was fetched
    news_cache[query] = (data, datetime.now())

    return jsonify(data), 200
