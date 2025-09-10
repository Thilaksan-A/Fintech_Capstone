from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db
from app.models import Watchlist
from app.utils.decorators import retry_request
from app.routes.crypto_information import get_top_ranking
from app.models.user import User

watchlist_bp = Blueprint("watchlist", __name__, url_prefix="/watchlist")


@watchlist_bp.route("/add", methods=["POST"])
@retry_request
def add_to_watchlist():
    data = request.get_json()
    user_id = data.get("user_id")
    symbol = data.get("symbol")

    existing = Watchlist.query.filter_by(
        user_id=user_id,
        symbol=symbol,
    ).first()
    if existing:
        return jsonify({"message": "Already in watchlist"}), 400

    new_watch = Watchlist(user_id=user_id, symbol=symbol)
    db.session.add(new_watch)
    db.session.commit()
    return jsonify({"message": "Added to watchlist"}), 201


@watchlist_bp.route("/list", methods=["GET"])
@jwt_required()
@retry_request
def get_watchlist():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401

    watchlist = Watchlist.query.filter_by(user_id=user_id).all()

    user = db.session.get(User, user_id)
    num_coins = 10
    match (user.subscription_tier):
        case "Free":
            num_coins = 3
        case "Medium":
            num_coins = 10
        case _:
            num_coins = 50

    print(user.subscription_tier)
    response, _ = get_top_ranking(set_rankings=num_coins)
    visible = {data["symbol"] for data in response.get_json()}

    crypto_list = [
        {
            "symbol": w.asset.symbol,
            "name": w.asset.name,
            "image": w.asset.image,
            "ranking": w.asset.ranking,
        }
        for w in watchlist
        if w.asset and w.symbol in visible
    ]
    return jsonify(crypto_list), 200


@watchlist_bp.route("/remove", methods=["POST"])
@retry_request
def remove_from_watchlist():
    data = request.get_json()
    user_id = data.get("user_id")
    symbol = data.get("symbol")

    entry = Watchlist.query.filter_by(user_id=user_id, symbol=symbol).first()
    if not entry:
        return jsonify({"message": "Not found in watchlist"}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Removed from watchlist"}), 200


@watchlist_bp.route("/toggle", methods=["POST"])
@jwt_required()
@retry_request
def toggle_watchlist():
    data = request.get_json()
    user_id = get_jwt_identity()
    symbol = data['symbol']
    print("Toggling watchlist for:", symbol)

    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401

    item = (
        db.session.query(Watchlist)
        .filter_by(user_id=user_id, symbol=symbol)
        .first()
    )
    if item:
        db.session.delete(item)
    else:
        db.session.add(Watchlist(user_id=user_id, symbol=symbol))

    db.session.commit()
    return jsonify(), 200


@watchlist_bp.route("/check", methods=["GET"])
@jwt_required()
@retry_request
def check_watchlist():
    user_id = get_jwt_identity()
    symbol = request.args.get("symbol", "").upper()

    if not user_id:
        return jsonify({"message": "User not authenticated"}), 401

    item = (
        db.session.query(Watchlist)
        .filter_by(user_id=user_id, symbol=symbol)
        .first()
    )
    if item:
        return jsonify({"isFavourited": True}), 200
    else:
        return jsonify({"isFavourited": False}), 200
