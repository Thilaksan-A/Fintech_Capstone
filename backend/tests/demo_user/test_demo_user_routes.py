import json
from tests.factories.demo_user import DemoUserFactory


def test_create_demo_user_route(client, session):
    payload = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "securepw",
        "risk_score": 3,
    }

    response = client.post(
        "/api/demo_user/",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 201

    data = response.get_json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data


def test_list_demo_users_route(client, session):
    # seed with 2 users
    users = DemoUserFactory.create_batch(size=2)

    response = client.get("/api/demo_user/")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2

    assert all("email" in u and "name" in u for u in data)
