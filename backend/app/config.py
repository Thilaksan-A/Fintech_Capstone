import logging
import sys

import app.env
from datetime import timedelta


class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',  # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m',  # Magenta
        'DATETIME': '\033[90m',  # Gray
        'NAME': '\033[96m',  # Cyan
    }
    RESET = '\033[0m'

    def format(self, record):
        record.shortname = record.name.split('.')[-1]
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        record.shortname = (
            f"{self.COLORS['NAME']}{record.shortname}{self.RESET}"
        )

        output = super().format(record)

        if record.asctime:
            output = output.replace(
                record.asctime,
                f"{self.COLORS['DATETIME']}{record.asctime}{self.RESET}",
            )
        return output


def configure_logging(debug=False) -> logging.Logger:
    level = logging.DEBUG if debug else logging.INFO
    log_format = "[%(asctime)s] <%(levelname)s::%(shortname)s> %(message)s"
    formatter = ColorFormatter(log_format, "%H:%M:%S")

    root_logger = logging.getLogger()

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured")
    return logger


class Config:
    FLASK_ENV = app.env.FLASK_ENV
    ENABLE_TIMESCALE_INIT = app.env.ENABLE_TIMESCALE_INIT
    SQLALCHEMY_DATABASE_URI = app.env.DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = app.env.JWT_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=23)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 20,
        'echo': False,  # Set to True for SQL query logging
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'safeguard_backend',
            'sslmode': 'require',
        },
    }


class TestingConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = app.env.TESTING_DATABASE_URL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0,
        'echo': False,  # Set to True for SQL query logging
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'safeguard_test',
            'sslmode': 'disable',  # Disable SSL for testing
        },
    }
