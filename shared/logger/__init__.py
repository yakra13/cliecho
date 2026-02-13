from pathlib import Path
from .logger import Logger
from .log_event import EventLevel
from .handler import ConsoleHandler, FileHandler

# 'Singleton' instance
_LOG = Logger()


def configure_logger(fh: FileHandler, ch: ConsoleHandler):
	_LOG.configure(fh, ch)

def log_warn(message: str) -> None:
	_LOG.log(EventLevel.WARN, message, {'file'})

def console_warn(message: str) -> None:
	_LOG.log(EventLevel.WARN, message, {'console'})

def warn_all(self, message: str) -> None:
	_LOG.log(EventLevel.WARN, message, {'file', 'console'})