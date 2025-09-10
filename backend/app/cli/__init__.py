from app.cli.cron import cron
from app.cli.demo import demo


def register_custom_commands(app):
    app.cli.add_command(cron)
    app.cli.add_command(demo)
