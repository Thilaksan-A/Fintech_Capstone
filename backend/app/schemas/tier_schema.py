from marshmallow import Schema, fields, validate


class TierSchema(Schema):
    tier = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "Free",
                "Medium",
                "Premium",
            ],
        ),
    )
