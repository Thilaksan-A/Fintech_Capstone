from .decorators import transactional, retry_request
from .filters import compose_filters
from pandas import Timestamp


def convert_timestamp_to_utc(ts: Timestamp) -> Timestamp:
    """
    Convert a pandas Timestamp to UTC timezone.
    """
    ts = Timestamp(ts)
    if ts.tzinfo is None:
        ts = ts.tz_localize('UTC')
    else:
        ts = ts.tz_convert('UTC')
    return ts.floor('h')


def model_to_dict(instance):
    return {
        column.name: getattr(instance, column.name)
        for column in instance.__table__.columns
    }


__all__ = [
    "transactional",
    "compose_filters",
    "retry_request",
    "model_to_dict",
]
