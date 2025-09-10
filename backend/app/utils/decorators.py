from functools import wraps
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from flask import jsonify
import logging

RETRY_ATTEMPTS = 3
logger = logging.getLogger(__name__)


def transactional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        session = db.session()
        try:
            # If a transaction is already active (e.g. in test), use a begin_nested
            if session.in_transaction():
                with session.begin_nested():
                    return fn(*args, **kwargs)
            else:
                with session.begin():
                    return fn(*args, **kwargs)
        except SQLAlchemyError as e:
            session.rollback()
            raise e

    return wrapper


def retry_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        error = None
        for attempt in range(RETRY_ATTEMPTS):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.info(f"Request failed - retried {attempt} times.")
                db.session.rollback()
                db.session.close()
                error = e

        logger.info(
            f"Request has been given up after retrying {attempt+1} times. "
            f"Error: {error}",
        )
        return jsonify({"error": "Request failed after retries"}), 500

    return wrapper
