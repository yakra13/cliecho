import logging
from logging.handlers import QueueHandler
from queue import Queue
from threading import Lock
from typing import Dict
from .formatters import JsonFormatter
from .context import get_context
from enum import Flag, auto

# Channels
class EventChannel(Flag):
	CONSOLE = auto()
	FILE = auto()

# Log levels
class EventLevel:
	DEBUG = "debug"
	INFO = "info"
	WARN = "warning"
	ERROR = "error"

# Core logger
_logger = logging.getLogger("app")
_logger.setLevel(logging.DEBUG)
_logger.propagate = False

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(logging.Formatter("%(message)s"))

_file_handlers: Dict[str, logging.FileHandler] = {}
_queue_handlers: Dict[int, QueueHandler] = {}
_lock = Lock()

# Global event queue per thread (for CLI consumption)
_EVENT_QUEUE: Any = None  # could be thread-local or contextvar

def set_event_queue(queue: Queue):
	global _EVENT_QUEUE
	_EVENT_QUEUE = queue

def _get_file_handler(ctx_id: str, ctx: dict) -> logging.FileHandler:
	"""
	TODO:
	"""
	if ctx_id in _file_handlers:
		return _file_handlers[ctx_id]
	fh = logging.FileHandler(f"{ctx['sanitized_name']}.log")
	fh.setFormatter(JsonFormatter())
	_file_handlers[ctx_id] = fh
	return fh

def _get_queue_handler(queue: Queue) -> QueueHandler:
	"""
	TODO:
	"""
	qid = id(queue)
	if qid in _queue_handlers:
		return _queue_handlers[qid]
	handler = QueueHandler(queue)
	_queue_handlers[qid] = handler
	return handler

def _route_log(level: str, message: str, channel: EventChannel, **kwargs):
	"""
	TODO:
	"""
	with _lock:
		ctx = get_context()
		ctx_id = ctx.get("id", "default")

		handlers_to_add = []

		if channel & EventChannel.FILE:
			fh = _get_file_handler(ctx_id, ctx)
			handlers_to_add.append(fh)

		if channel & EventChannel.CONSOLE:
			if _EVENT_QUEUE:
				qh = _get_queue_handler(_EVENT_QUEUE)
				handlers_to_add.append(qh)
			else:
				handlers_to_add.append(_console_handler)

		# Temporarily attach handlers
		for h in handlers_to_add:
			_logger.addHandler(h)
		try:
			_logger.log(getattr(logging, level.upper()), message, extra={"data": kwargs})
		finally:
			# Remove temporary handlers to avoid duplicates
			for h in handlers_to_add:
				if h not in (_console_handler,):
					_logger.removeHandler(h)

# Route classes
class _Route:
	"""
	TODO:
	"""
	CHANNEL: EventChannel

	@classmethod
	def debug(cls, msg: str, **kwargs):
		"""
		TODO:
		"""
		_route_log("debug", msg, cls.CHANNEL, **kwargs)

	@classmethod
	def info(cls, msg: str, **kwargs):
		"""
		TODO:
		"""
		_route_log("info", msg, cls.CHANNEL, **kwargs)

	@classmethod
	def warn(cls, msg: str, **kwargs):
		"""
		TODO:
		"""
		_route_log("warning", msg, cls.CHANNEL, **kwargs)

	@classmethod
	def error(cls, msg: str, **kwargs):
		"""
		TODO:
		"""
		_route_log("error", msg, cls.CHANNEL, **kwargs)

class Console(_Route):
	"""
	TODO:
	"""
	CHANNEL = EventChannel.CONSOLE

class Log(_Route):
	"""
	TODO:
	"""
	CHANNEL = EventChannel.FILE

class ConsoleLog(_Route):
	"""
	TODO:
	"""
	CHANNEL = EventChannel.CONSOLE | EventChannel.FILE
