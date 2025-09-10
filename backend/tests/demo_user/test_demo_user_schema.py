from app.schemas.demo_user import DemoUserSchema
from tests.factories.demo_user import DemoUserFactory


def test_demo_user_schema_serialization():
    user = DemoUserFactory.build(id=1)  # don't persist
    schema = DemoUserSchema()
    result = schema.dump(user)

    assert result["id"] == 1
    assert result["name"] == user.name
    assert result["email"] == user.email
    assert result["password"] == user.password
    assert result["risk_score"] == user.risk_score


def test_demo_user_schema_deserialization():
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "securepw",
        "risk_score": 3,
    }

    schema = DemoUserSchema()
    result = schema.load(payload)

    assert result["name"] == "Test User"
    assert result["email"] == "test@example.com"
    assert result["password"] == "securepw"
    assert result["risk_score"] == 3
