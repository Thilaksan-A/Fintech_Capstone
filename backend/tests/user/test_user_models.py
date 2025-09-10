from app.constants.user import InvestorType, SocialImpact, TimeScore
from app.models.user import User
from tests.factories.user import UserFactory, UserProfileFactory


def test_user_creation(session):
    user = UserFactory()

    assert isinstance(user, User)
    assert user.id is not None
    assert user.username is not None
    assert user.password_hash is not None
    assert user.email is not None
    assert user.is_active is True
    assert user.profile is None

    db_user = session.query(User).filter_by(id=user.id).first()
    assert db_user is not None


def test_user_with_profile_creation(session):
    user = UserFactory.create(
        username="testuser",
        email="testuser@example.com",
        password_hash="hashed_password",
        is_active=True,
    )
    profile = UserProfileFactory.create(user=user)

    # Verify user is linked correctly
    assert user.profile == profile
    assert profile.user == user
    assert user.profile.id == profile.id


def test_user_profile_creation(session):
    profile = UserProfileFactory.create(
        risk_score=5,
        time_score=TimeScore.MEDIUM,
        social_impact=SocialImpact.HIGH,
        investor_type=InvestorType.DATA_DRIVEN_STRATEGIST,
        raw_responses={"q1": "yes"},
    )

    # Verify user is linked correctly
    assert profile.user is not None
    assert profile.user.profile == profile

    # Verify fields
    assert profile.risk_score == 5
    assert profile.time_score.name == "MEDIUM"
    assert profile.social_impact.name == "HIGH"
    assert profile.investor_type.name == "DATA_DRIVEN_STRATEGIST"
    assert profile.raw_responses["q1"] == "yes"
