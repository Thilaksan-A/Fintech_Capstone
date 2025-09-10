import factory
from app.models.demo_user import DemoUser
from tests.factories import BaseFactory


class DemoUserFactory(BaseFactory):
    class Meta:
        model = DemoUser

    name = factory.Faker("name")
    email = factory.Faker("email")
    password = factory.Faker("password")
    risk_score = factory.Faker("random_int", min=0, max=100)
