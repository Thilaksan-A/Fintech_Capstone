import click

from app.models.demo_user import DemoUser
from app.extensions import db

# CLI command group for demo-related commands
# TODO: deprecate this before production release


@click.group()
def demo():
    """Demo commands."""
    pass


@demo.command("create_user")
@click.option("--name", prompt="User name", help="Name of the demo user.")
@click.option("--email", prompt="User email", help="Email of the demo user.")
@click.option(
    "--password",
    prompt="User password",
    help="Password of the demo user.",
)
@click.option(
    "--risk-score",
    default=50,
    help="Risk score of the demo user (default: 50).",
)
def create_user(name, email, password, risk_score):
    """Create a demo user."""
    if DemoUser.query.filter_by(email=email).first():
        click.echo(f"User with email {email} already exists.")
        return

    user = DemoUser(
        name=name,
        email=email,
        password=password,
        risk_score=risk_score,
    )
    db.session.add(user)
    db.session.commit()
    click.echo(f"User {user.name} created successfully with ID {user.id}.")


@demo.command("get_users")
def get_users():
    """Get all demo users.(for testing purposes)"""
    users = DemoUser.query.all()
    click.echo(f"Retrieved {len(users)} users.")
    for user in users:
        click.echo(
            f"User: {user.name}, Email: {user.email}, Risk Score: {user.risk_score}",
        )
