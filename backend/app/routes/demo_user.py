from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.demo_user import DemoUser
from app.schemas.demo_user import DemoUserSchema
from marshmallow import ValidationError

demo_user_bp = Blueprint("demo_user", __name__)
demo_user_schema = DemoUserSchema()
demo_user_list_schema = DemoUserSchema(many=True)


@demo_user_bp.route("/", methods=["POST"])
def create_demo_user():
    data = request.get_json()
    try:
        user_data = demo_user_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    new_user = DemoUser(**user_data)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(demo_user_schema.dump(new_user)), 201


@demo_user_bp.route("/", methods=["GET"])
def list_demo_users():
    users = DemoUser.query.all()
    return jsonify(demo_user_list_schema.dump(users))
