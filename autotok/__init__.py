import typing as t

import logging
from logging.handlers import RotatingFileHandler

from datetime import datetime
from pathlib import Path



TIME_FORMAT = r'%m-%d-%Y_%H-%M-%S'
now: t.Callable[[], str] = lambda: datetime.now().strftime(TIME_FORMAT)

MODULE_ROOT = Path(__file__).parent.absolute()
DOWNLOADS_ROOT = MODULE_ROOT.parent / 'downloads'



LOGS_ROOT = MODULE_ROOT / 'logs'
LOGS_ROOT.mkdir(exist_ok=True)

LOGGING_HANDLERS: list[logging.Handler] = [
    RotatingFileHandler(LOGS_ROOT / f'autotok.log', maxBytes=20 * 1024 * 1024, backupCount=7, encoding='utf-8'),
    logging.StreamHandler()
]


LOGGER = logging.getLogger(MODULE_ROOT.stem)
LOGGER.setLevel(logging.INFO)

for handler in LOGGING_HANDLERS:
    handler.setFormatter(logging.Formatter('%(name)s (%(asctime)s) [%(levelname)s]: %(message)s'))
    LOGGER.addHandler(handler)
