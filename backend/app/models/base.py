from app.extensions import db
from sqlalchemy import select


class BaseModel(db.Model):
    __abstract__ = True

    @classmethod
    def get_or_create(cls, defaults=None, **kwargs):
        with db.session.no_autoflush:
            instance = db.session.execute(
                select(cls).filter_by(**kwargs),
            ).scalar_one_or_none()
            if instance:
                return instance

            params = dict(kwargs)
            if defaults:
                params.update(defaults)
            instance = cls(**params)
            db.session.add(instance)

        return instance
