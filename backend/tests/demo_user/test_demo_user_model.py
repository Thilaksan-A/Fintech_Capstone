import factory
from app.models.demo_user import DemoUser
from tests.factories.demo_user import DemoUserFactory


def test_demo_user_creation_and_fields(session):
    """Test DemoUser model field values and DB persistence."""
    user = DemoUserFactory(
        email="alice@example.com",
        name="Alice",
        password="supersecret",
        risk_score=3,
    )

    # Fetch from DB to confirm persistence
    fetched_user = (
        session.query(DemoUser).filter_by(email="alice@example.com").first()
    )

    assert fetched_user is not None
    assert fetched_user.name == "Alice"
    assert fetched_user.email == "alice@example.com"
    assert fetched_user.password == "supersecret"
    assert fetched_user.risk_score == 3


def test_another_demo_user_model(session):
    # This test ensures previous test data doesn't persist
    DemoUserFactory.create_batch(
        size=3,
        email=factory.Iterator(
            ["john@example.com", "ethan@gmail.com", "tiny@ad.unsw.edu.au"],
        ),
        name=factory.Iterator(["John", "Ethan", "Tiny"]),
        risk_score=3,
    )

    result = (
        session.query(DemoUser).filter_by(email="alice@example.com").first()
    )
    assert result is None

    total = session.query(DemoUser).count()
    assert total == 3
