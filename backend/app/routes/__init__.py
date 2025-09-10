from .user import user_bp
from .demo_user import demo_user_bp
from .crypto_information import crypto_bp
from .watchlist import watchlist_bp
from .health import health_bp


def register_blueprints(app):
    app.register_blueprint(demo_user_bp, url_prefix="/api/demo_user")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(crypto_bp, url_prefix="/api/crypto")
    app.register_blueprint(watchlist_bp, url_prefix="/api/watchlist")
    app.register_blueprint(health_bp, url_prefix="/api/health")
