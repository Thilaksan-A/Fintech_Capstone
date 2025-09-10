from flask import Flask
from flask_cors import CORS
from urllib.parse import urlparse, urlunparse
from sqlalchemy import text
from celery import Celery, Task

from app.cli import register_custom_commands
from app.extensions import db, ma, migrate, jwt_manager
from app.config import Config, TestingConfig, configure_logging
from app.routes import register_blueprints
from app.env import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app


def mask_db_uri(db_uri) -> str:
    parsed_uri = urlparse(db_uri)
    username = '***' if parsed_uri.username else ''
    password = '***' if parsed_uri.password else ''
    masked_netloc = (
        f"{username}:{password}@{parsed_uri.hostname}:{parsed_uri.port}"
    )
    masked_uri = urlunparse(
        (
            parsed_uri.scheme,
            masked_netloc,
            parsed_uri.path,
            parsed_uri.params,
            parsed_uri.query,
            parsed_uri.fragment,
        ),
    )
    return masked_uri


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    configure_logging(app.debug)
    if testing:
        app.logger.info("Starting test instance")
        app.config.from_object(TestingConfig)
    else:
        app.logger.info("Starting development instance")
        app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    jwt_manager.init_app(app)

    # Now initialize TimescaleDB within app context
    if not testing and app.config.get("ENABLE_TIMESCALE_INIT"):
        with app.app_context():
            try:
                db.session.execute(
                    text("CREATE EXTENSION IF NOT EXISTS timescaledb;"),
                )
                db.session.commit()
                app.logger.info("TimescaleDB extension ensured.")
            except Exception as e:
                app.logger.error("Could not ensure TimescaleDB: %s", e)

    # Log database URI after db is initialized
    if not testing:
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri:
            masked_uri = mask_db_uri(db_uri)
            app.logger.info("SQLALCHEMY_DATABASE_URI: %s", masked_uri)
            app.logger.info(
                "SQLALCHEMY_ENGINE_OPTIONS: %s",
                app.config['SQLALCHEMY_ENGINE_OPTIONS'],
            )

    app.config.from_mapping(
        CELERY=dict(
            broker_url=CELERY_BROKER_URL,
            result_backend=CELERY_RESULT_BACKEND,
            task_ignore_result=True,
            include=[
                'app.services.market.tasks',
                'app.services.sentiment.tasks',
            ],
            timezone='Australia/Sydney',
            enable_utc=False,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    app.logger.info("FLASK_ENV: %s", app.config['FLASK_ENV'])
    CORS(app)

    register_blueprints(app)
    register_custom_commands(app)

    return app
