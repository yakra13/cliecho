from pathlib import Path
from typing import Any, Callable, Dict, Generic, Mapping, TypeVar
from .formatter import Formatter, Verbosity
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


T = TypeVar("T")

# class MetadataConfig:
#     def __init__(self, apply):
#         self._data: Dict[str, object] = {}
#         self._apply = apply

#     def update(self, **kwargs):
#         self._data.update(kwargs)
#         self._apply(self._data)

#     def __setattr__(self, key, value):
#         if key.startswith("_"):
#             super().__setattr__(key, value)
#             return

#         self._data[key] = value
#         self._apply(self._data)

#     def __getattr__(self, key):
#         return self._data[key]

#     def as_dict(self):
#         return dict(self._data)


SetterFn = Callable[[str, Any], None]

class AttributeProxy:
	def __init__(self,
			  	 setter: SetterFn,
				 getter: Callable[[str], Any] | None = None):
		object.__setattr__(self, '_setter', setter)
		object.__setattr__(self, '_getter', getter)

	def __setattr__(self, key: str, value: Any) -> None:
		self._setter(key, value)

	def __getattr__(self, key: str) -> Any:
		if self._getter:
			return self._getter(key)
		raise AttributeError(key)

class MetadataProxy(AttributeProxy):
	current_user: str
	current_host: str
	# def __init__(self, logger):
	# 	object.__setattr__(self, "_logger", logger)

	# def __setattr__(self, key: str, value: Any) -> None:
	# 	self._logger.set_metadata(**{key: value})

	# def __getattr__(self, key: str) -> Any:
	# 	return self._logger._metadata.get(key)

class ConfigValue(Generic[T]):
	def __init__(self, name: str, setter: Callable[[T], None]):
		self.name = name
		self.setter = setter
		# self._value = None

	def __get__(self, obj, owner) -> T:
		# if self._value is None:
		# 	self._value = self.setter()
		# return self._value
		raise AttributeError(f"{self.name} is write-only")

	def __set__(self, instance, value: T) -> None:
		self.setter(value)

# class ConfigValue:
#     def __init__(self, name, apply):
#         self.name = name
#         self.apply = apply
#         self._value = None

#     def __get__(self, obj, owner):
#         return self._value

#     def __set__(self, obj, value):
#         self._value = value
#         self.apply(value)

Metadata = Mapping[str, str]
class LogConfig:
	log_directory: ConfigValue[Path] = ConfigValue("log_directory", lambda v: _LOG.set_log_path(v))
	# console_verbosity: ConfigValue = ConfigValue("console_verbosity", lambda v: _LOG.set_verbosity(v))
	console_formatter: ConfigValue[Formatter] = ConfigValue("console_formatter", lambda v: _LOG.set_console_formatter(v))
	file_formatter: ConfigValue[Formatter] = ConfigValue("file_formatter", lambda v: _LOG.set_file_formatter(v))
	verbosity: ConfigValue[Verbosity] = ConfigValue("verbosity", lambda v: _LOG.set_verbosity(v))
	# metadata: ConfigValue[Metadata] = ConfigValue("metadata", lambda: MetadataConfig(lambda d: _LOG.set_metadata(**d)))
	metadata = MetadataProxy(_LOG.set_metadata, _LOG.get_metadata)


	# @staticmethod
	# def console_formatter(formatter: Formatter) -> None:
	# 	_LOG.set_console_formatter(formatter)

	# @staticmethod
	# def file_formatter(formatter: Formatter) -> None:
	# 	_LOG.set_file_formatter(formatter)

	# @staticmethod
	# def log_path(path: Path) -> None:
	# 	_LOG.set_log_path(path)

# # @staticmethod
# def set_metadata(named_arg, *args, **kwargs) -> None:
# 	print()

# set_metadata(1, 1, 2, keyword=1, keyword2=3)