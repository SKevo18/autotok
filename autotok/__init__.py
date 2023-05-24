import typing as t

from datetime import datetime
from pathlib import Path


TIME_FORMAT = r'%m-%d-%Y_%H-%M-%S'
now: t.Callable[[], str] = lambda: datetime.now().strftime(TIME_FORMAT)

MODULE_ROOT = Path(__file__).parent.absolute()
DOWNLOADS_ROOT = MODULE_ROOT.parent / 'downloads'
