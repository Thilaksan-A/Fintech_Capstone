import pytest
from app import create_app, db as _db
from sqlalchemy.orm import sessionmaker, scoped_session


@pytest.fixture(scope="session")
def app():
    app = create_app(testing=True)
    print(f"TEST DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def connection(app):
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        yield connection
        if transaction.is_active:
            transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def session(connection):
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="function")
def db_session(connection):
    _db.session = scoped_session(sessionmaker(bind=connection))
    yield _db.session
    _db.session.remove()


@pytest.fixture(scope="function")
def client(app, db_session):
    with app.app_context():
        with app.test_client() as client:
            yield client


@pytest.fixture(scope="function", autouse=True)
def bind_factory_session(db_session):
    from tests.factories import BaseFactory

    BaseFactory._meta.sqlalchemy_session = db_session


@pytest.fixture(scope="function")
def test_user(app, db_session):
    # Ensure a test user exists for authentication.
    from app.models.user import User

    user = db_session.query(User).filter_by(email="test@example.com").first()
    if not user:
        # supply both username and email to satisfy NOT NULL constraints
        user = User(username="testuser", email="test@example.com")
        user.set_password("password")
        db_session.add(user)
        db_session.commit()

    return user


@pytest.fixture(scope="function")
def access_token(app, test_user):
    from flask_jwt_extended import create_access_token

    with app.app_context():
        return create_access_token(identity=str(test_user.id))
