from enum import Flag, auto
from queue import Queue
import threading
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Set
# from dataclasses import asdict, dataclass, field
# from datetime import datetime, timezone
# from enum import Enum, auto

from log_event import EventLevel, EventLog, EventChannel
from handler import FileHandler, ConsoleHandler, QueueHandler
from context import Context, normalize_context
from formatter import Formatter, JsonFormatter, ConsoleFormatter

_EVENT_QUEUE: ContextVar[Queue] = ContextVar("event_queue")
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
		_LOG_CONTEXT.reset(token)


class Logger:
	def __init__(self):
		self._io_lock: threading.Lock = threading.Lock()
		# self._log_dir: Path # TODO
		# self._file_handler: FileHandler
		self._console_out_handler: ConsoleHandler
		# self._console_err_handler: ConsoleHandler
		self._is_configured: bool = False
		self._file_handlers: Dict[str, FileHandler] = {}
		self._queue_handlers: Dict[int, QueueHandler] = {}

		self._console_formatter: Formatter = ConsoleFormatter()
		self._file_formatter: Formatter = JsonFormatter()
		self._logging_path: Path = Path() # TODO: get logging path

		self._metadata: Dict[str, Any] = {}

	def _close_context(self, id: str) -> None:
		with self._io_lock:
			handler: Optional[FileHandler] = self._file_handlers.pop(id, None)

			if handler is None:
				return
			
			try:
				handler.close()
			except Exception:
				pass # NOTE: optional ignore errors on close

	def _create_file_handler(self, ctx: Dict[str, Any]) -> FileHandler:
		# f = FileHandler(self._file_formatter, Path(''))
		file_name: str = ctx.get('name', 'default')
		full_path: Path = self._logging_path / file_name
		return FileHandler(self._file_formatter, full_path)

	def set_console_formatter(self, formatter: Formatter = ConsoleFormatter()):
		self._console_formatter = formatter

	def set_file_formatter(self, formatter: Formatter = JsonFormatter()):
		self._file_formatter = formatter

	def set_log_path(self, path: Path) -> None:
		# TODO: validation
		self._logging_path = path

	def set_metadata(self, **kwargs) -> None:
		self._metadata.update(kwargs)

	def log(self, event_level: EventLevel, message: str, channel: EventChannel) -> None:
		with self._io_lock:
			event = EventLog(event_level, message)

			ctx = _LOG_CONTEXT.get()
			if ctx:
				# TODO: where to stick username and hostname info for logging to file
				event.metadata.update(ctx)
				# merge logger metadata into each log entry
				event.metadata.update(self._metadata)

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
					self._console_out_handler.emit(event)
