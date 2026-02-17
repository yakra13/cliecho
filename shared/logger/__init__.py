from .formatter import Formatter
from .logger import Logger as _Logger
from .logger import EventChannel, event_queue, logging_context
from .log_event import EventLevel

__all__ = [
	"event_queue",
	"logging_context",
	"Console",
	"Log",
	"ConsoleLog"
]

# 'Singleton' instance
_LOG = _Logger()


class _Route:
	CHANNEL: EventChannel

	@classmethod
	def debug(cls, message: str) -> None:
		_LOG.log(EventLevel.DEBUG, message, cls.CHANNEL)

	@classmethod
	def error(cls, message: str) -> None:
		_LOG.log(EventLevel.ERROR, message, cls.CHANNEL)

	@classmethod
	def info(cls, message: str) -> None:
		_LOG.log(EventLevel.INFO, message, cls.CHANNEL)

	@classmethod
	def warn(cls, message: str) -> None:
		_LOG.log(EventLevel.WARN, message, cls.CHANNEL)


class Console(_Route):
	CHANNEL = EventChannel.CONSOLE


class Log(_Route):
	CHANNEL = EventChannel.FILE


class ConsoleLog(_Route):
	CHANNEL = EventChannel.CONSOLE | EventChannel.FILE

class LogConfig:
	@staticmethod
	def console_formatter(formatter: Formatter) -> None:
		_LOG.set_console_formatter(formatter)

	@staticmethod
	def file_formatter(formatter: Formatter) -> None:
		_LOG.set_file_formatter(formatter)