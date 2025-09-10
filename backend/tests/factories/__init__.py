from factory.alchemy import SQLAlchemyModelFactory


class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True

        # Use a lambda to lazily fetch the session from the BaseFactory at runtime.
        # This avoids issues where the factory is imported before pytest assigns the test session.
        sqlalchemy_session_factory = staticmethod(
            lambda: BaseFactory._meta.sqlalchemy_session,
        )

        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"
