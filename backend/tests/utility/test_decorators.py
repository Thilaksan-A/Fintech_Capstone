import pytest
from sqlalchemy import text
from app.extensions import db
from app.models.demo_user import DemoUser
from app.utils.decorators import transactional
from tests.factories.demo_user import DemoUserFactory


# Function that should succeed
@transactional
def create_demo_user():
    DemoUserFactory()


# Function that should fail and trigger rollback
@transactional
def create_demo_user_and_fail():
    DemoUserFactory()
    raise Exception("Force rollback")


def test_transactional_success():
    create_demo_user()
    assert db.session.query(DemoUser).count() == 1


def test_transactional_rollback_on_error():
    DemoUserFactory()  # Create one user first
    initial_count = db.session.query(DemoUser).count()

    with pytest.raises(Exception, match="Force rollback"):
        create_demo_user_and_fail()

    # Count shouldn't change
    assert db.session.query(DemoUser).count() == initial_count


def test_transactional_without_active_transaction(app):
    with app.app_context():
        # Temporarily remove session-level transaction
        db.session.remove()

        called = {"executed": False}

        @transactional
        def insert_something():
            called["executed"] = True
            db.session.execute(text("SELECT 1"))

        insert_something()
        assert called["executed"]


def test_transactional_without_active_transaction_and_fails(app):
    with app.app_context():
        # Temporarily remove session-level transaction
        db.session.remove()

        called = {"executed": False}

        @transactional
        def insert_something():
            called["executed"] = True
            db.session.add(DemoUserFactory.build())
            raise Exception("Force failure")

        with pytest.raises(Exception, match="Force failure"):
            insert_something()
        assert db.session.query(DemoUser).count() == 0
