import factory
from app.models.user import User, UserProfile
from app.constants.user import InvestorType, SocialImpact, TimeScore
from tests.factories import BaseFactory


class UserFactory(BaseFactory):
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password_hash = factory.Faker("password")


class UserProfileFactory(BaseFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(UserFactory)

    risk_score = 5
    rational_score = 4
    fomo_score = 2
    emotional_score = 3
    time_score = TimeScore.MEDIUM
    social_impact = SocialImpact.HIGH
    investor_type = InvestorType.DATA_DRIVEN_STRATEGIST
    raw_responses = {"q1": "yes", "q2": "no"}
