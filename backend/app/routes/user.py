from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from app.extensions import db
from app.models.user import User, UserProfile
from app.schemas.user_schema import UserSchema
from app.schemas.survey_schema import SurveySchema
from app.services.user_profile import (
    calculate_user_profile_scores,
    classify_user_profile,
    USER_PROFILE_SCORING_MAP,
)
from app.constants.survey import ScoreType
from app.schemas.tier_schema import TierSchema
from marshmallow import ValidationError
from app.utils.decorators import retry_request

user_bp = Blueprint("user", __name__)
user_schema = UserSchema()
survey_schema = SurveySchema()
tier_schema = TierSchema()


@user_bp.route("/login", methods=["POST"])
@retry_request
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get("email")).first()  # type: ignore
    if not user:
        return jsonify(msg="User not found"), 404

    if not user.check_password(data.get("password", "")):
        return jsonify(msg="Invalid credentials"), 401
    token = create_access_token(identity=str(user.id))
    return jsonify(access_token=token), 200


@user_bp.route("/", methods=["POST"])
@retry_request
def create_user():
    data = request.get_json()
    try:
        user_data = user_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    if User.query.filter_by(email=user_data["email"]).first():
        return jsonify(msg="Email already exists"), 400

    new_user = User(**user_data)
    new_user.set_password(user_data["password_hash"])
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)

    return (
        jsonify(
            {"user": user_schema.dump(new_user), "access_token": access_token},
        ),
        201,
    )


@user_bp.route("/survey", methods=["POST"])
@jwt_required()
@retry_request
def submit_survey():
    data = request.get_json() or {}
    try:
        answers = survey_schema.load(data)
    except ValidationError as err:
        return jsonify(error=err.messages), 400

    scores = calculate_user_profile_scores(answers, USER_PROFILE_SCORING_MAP)
    time_enum, social_enum, inv_enum = classify_user_profile(scores)
    user_id = get_jwt_identity()

    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.session.add(profile)

    profile.risk_score = scores[ScoreType.RISK]
    profile.emotional_score = scores[ScoreType.EMOTIONAL]
    profile.rational_score = scores[ScoreType.RATIONAL]
    profile.fomo_score = scores[ScoreType.FOMO]

    profile.time_score = time_enum
    profile.social_impact = social_enum
    profile.investor_type = inv_enum
    profile.raw_responses = answers

    db.session.commit()
    scores_dict = {st.value: val for st, val in scores.items()}
    return (
        jsonify(
            {
                "scores": scores_dict,
                "time_score": time_enum.value,
                "social_impact": social_enum.value,
                "investor_type": inv_enum.value,
            },
        ),
        200,
    )


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
@retry_request
def get_profile():
    profile = UserProfile.query.filter_by(user_id=get_jwt_identity()).first()
    if not profile:
        return jsonify({}), 200

    return (
        jsonify(
            {
                'risk_score': profile.risk_score,
                'rational_score': profile.rational_score,
                'emotional_score': profile.emotional_score,
                'fomo_score': profile.fomo_score,
                'time_score': profile.time_score.value,
                'social_impact': profile.social_impact.value,
                'investor_type': profile.investor_type.value,
                'raw_responses': profile.raw_responses,
            },
        ),
        200,
    )


@user_bp.route("/authorise", methods=["GET"])
@jwt_required()
@retry_request
def check_jwt():
    return jsonify({}), 201


@user_bp.route("/tier", methods=["GET"])
@jwt_required()
@retry_request
def get_tier():
    user = User.query.filter(User.id == get_jwt_identity()).first()
    if not user:
        return jsonify({}), 401

    limit = 0
    if user.subscription_tier == "Free":
        limit = 3
    elif user.subscription_tier == "Medium":
        limit = 10
    else:
        limit = 50

    return (
        jsonify(
            {
                'subscription_tier': user.subscription_tier,
                'limit': limit,
            },
        ),
        200,
    )


@user_bp.route("/update_tier", methods=["POST"])
@jwt_required()
@retry_request
def update_tier():
    data = request.get_json() or {}
    try:
        tier = tier_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    user = User.query.filter(User.id == get_jwt_identity()).first()
    if not user:
        return jsonify({}), 401
    user.subscription_tier = tier["tier"]
    db.session.commit()
    return (
        jsonify(
            {'subscription_tier': user.subscription_tier},
        ),
        200,
    )


@user_bp.route("/user_data", methods=["GET"])
@jwt_required()
def user_data():
    user_id = get_jwt_identity()

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"username": user.username, "email": user.email}), 200
