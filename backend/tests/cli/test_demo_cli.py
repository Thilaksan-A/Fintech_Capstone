import pytest
from click.testing import CliRunner
from app.cli.demo import create_user, get_users
from app.models.demo_user import DemoUser
from tests.factories.demo_user import DemoUserFactory


def test_get_users_command(app):
    runner = CliRunner()

    DemoUserFactory(
        name="Alice",
        email="alice@example.com",
        password="password123",
        risk_score=42,
    )
    DemoUserFactory(
        name="Bob",
        email="bob@example.com",
        password="password123",
        risk_score=88,
    )

    result = runner.invoke(get_users)

    assert result.exit_code == 0
    assert "Retrieved 2 users." in result.output
    assert "Alice" in result.output
    assert "Bob" in result.output


def test_get_users_no_users(app):
    runner = CliRunner()

    result = runner.invoke(get_users)

    assert result.exit_code == 0


def test_create_user_command(app):
    runner = CliRunner()

    result = runner.invoke(
        create_user,
        [
            "--name",
            "Charlie",
            "--email",
            "charlie@example.com",
            "--password",
            "password123",
            "--risk-score",
            "75",
        ],
    )

    assert result.exit_code == 0
    assert "User Charlie created successfully" in result.output
