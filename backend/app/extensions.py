from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate


class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True


db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
jwt_manager = JWTManager()
