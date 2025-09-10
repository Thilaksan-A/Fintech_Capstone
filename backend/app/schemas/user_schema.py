from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    username = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=64),
    )
    email = fields.Email(required=True)
    password_hash = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=6),
    )
