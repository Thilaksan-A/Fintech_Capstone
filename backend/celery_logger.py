from datetime import datetime
import logging
from zoneinfo import ZoneInfo
from app.config import ColorFormatter

from celery.signals import after_setup_task_logger, after_setup_logger


class SydneyColorFormatter(ColorFormatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(
            record.created,
            ZoneInfo("Australia/Sydney"),
        )
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()


@after_setup_task_logger.connect
def after_setup_celery_task_logger(logger, **kwargs):
    logger.handlers.clear()
    formatter = SydneyColorFormatter(
        '%(levelname)s %(asctime)s [%(processName)s]'
        '%(task_name)s[%(task_id)s]: %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%Z',
    )
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)
    logger.propagate = False


@after_setup_logger.connect
def after_setup_celery_logger(logger, **kwargs):
    logger.handlers.clear()
    formatter = SydneyColorFormatter(
        '%(levelname)s %(asctime)s [%(processName)s] %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S%Z',
    )
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)
    logger.propagate = False
