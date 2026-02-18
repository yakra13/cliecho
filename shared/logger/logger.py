# from enum import Flag, auto
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from queue import Queue
from typing import Any, Dict, Optional
# from dataclasses import asdict, dataclass, field
# from datetime import datetime, timezone
# from enum import Enum, auto

from .log_event import EventLevel, EventLog, EventChannel
from .handler import FileHandler, ConsoleHandler, QueueHandler
from .context import Context, normalize_context
from .formatter import AnsiConsoleFormatter, Formatter, JsonFormatter, ConsoleFormatter, Verbosity

_EVENT_QUEUE: ContextVar[Optional[Queue]] = ContextVar("event_queue", default=None)
_LOG_CONTEXT: ContextVar[Dict[str, Any]] = ContextVar("log_context", default={})

@contextmanager
def event_queue(queue: Queue):
	token = _EVENT_QUEUE.set(queue)

	try:
		yield
	finally:
		_EVENT_QUEUE.reset(token)

@contextmanager
def logging_context(context: Optional[Context] = None, **kwargs: Any):
	current = _LOG_CONTEXT.get()

	merged = {**current}

	if context:
		merged.update(normalize_context(context))
	# new_context = {**current, **kwargs}	

	merged.update(kwargs)
	
	token = _LOG_CONTEXT.set(merged)

	try:
		yield
	finally:
		ctx_id = merged.get("id", "default")
		Logger._close_context(ctx_id)
		_LOG_CONTEXT.reset(token)


class Logger:
	log_extension: str = ".log"
	log_directory: Path = Path("/home/joshua.ziebarth/Documents")
	file_formatter: Formatter = JsonFormatter()
	file_handlers: Dict[str, FileHandler] = {}
	_lock: threading.Lock = threading.Lock()

	def __init__(self):
		# self._lock: threading.Lock = threading.Lock()

		self._console_formatter: Formatter = AnsiConsoleFormatter(verbosity=Verbosity.DEBUG)
		self._file_formatter: Formatter = JsonFormatter()

		self._console_handler: ConsoleHandler = ConsoleHandler(self._console_formatter)
		self._file_handlers: Dict[str, FileHandler] = {}
		self._queue_handlers: Dict[int, QueueHandler] = {}

		self._logging_path: Path = Path() # TODO: get logging path
		self._log_directory: str = '.log'
		self._metadata: Dict[str, Any] = {}

	@classmethod
	def _close_context(cls, id: str) -> None:
		with cls._lock:
			handler: Optional[FileHandler] = cls.file_handlers.pop(id, None)

			if handler is None:
				return
			
			try:
				handler.close()
			except Exception:
				pass # NOTE: optional ignore errors on close

	def _create_file_handler(self, ctx: Dict[str, Any]) -> FileHandler:
		id: str = ctx.get('id', 'default')
		file_name: str = id + self.log_extension
		full_path: Path = self.log_directory / file_name

		handler = FileHandler(self.file_formatter, full_path)
		self.file_handlers[id] = handler
		return handler

	def set_console_formatter(self, formatter: Formatter = ConsoleFormatter()):
		self._console_formatter = formatter

	def set_file_formatter(self, formatter: Formatter = JsonFormatter()):
		self._file_formatter = formatter

	def set_log_path(self, path: Path) -> None:
		# TODO: validation
		self._logging_path = path

	def get_metadata(self, key: str) -> Any:
		return self._metadata.get(key, None)

	def set_metadata(self, key: str, value: Any) -> None:
		self._metadata.update({key: value})

	def set_verbosity(self, verbosity: Verbosity) -> None:
		# self._verbosity = verbosity
		self._console_formatter.update_verbosity(verbosity)

	def log(self, event_level: EventLevel, message: str, channel: EventChannel) -> None:
		with self._lock:
			event = EventLog(event_level, message)

			ctx = _LOG_CONTEXT.get()
			if ctx:
				event.merge_metadata(self._metadata, ctx)
				# TODO: where to stick username and hostname info for logging to file
				# event.metadata.update(ctx)
				# merge logger metadata into each log entry
				# event.metadata.update(self._metadata)

			if channel & EventChannel.FILE:
				ctx_id = ctx.get('id', 'default')

				handler = self._file_handlers.get(ctx_id)

				if handler is None:
					handler = self._create_file_handler(ctx)
					self._file_handlers[ctx_id] = handler

				handler.emit(event)

			if channel & EventChannel.CONSOLE:
				queue: Optional[Queue] = _EVENT_QUEUE.get()

				if queue is not None:
					# Write to the queue to be displayed in the console later
					qid = id(queue)
					handler = self._queue_handlers.get(qid)

					if handler is None:
						handler = QueueHandler(self._console_formatter, queue)
						self._queue_handlers[qid] = handler
					
					handler.emit(event)
				else:
					# Write immediately to the console
					self._console_handler.emit(event)
