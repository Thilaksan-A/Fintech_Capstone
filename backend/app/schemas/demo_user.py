from app.extensions import ma
from app.models.demo_user import DemoUser


class DemoUserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DemoUser

    id = ma.auto_field()
    name = ma.auto_field()
    email = ma.auto_field()
    password = ma.auto_field()
    risk_score = ma.auto_field()
