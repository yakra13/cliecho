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

		self._console_formatter: Formatter
		self._file_formatter: Formatter
		self._logging_path: Path = Path() # TODO: get logging path

		self.set_console_formatter()
		self.set_file_formatter()

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

	# def configure(self, file_handler: FileHandler, console_handler: ConsoleHandler) -> None:
	# 	if self._is_configured:
	# 		raise RuntimeError("Logger already configured")

	# 	self._file_handler = file_handler
	# 	self._console_out_handler = console_handler

	# 	self._is_configured = True

	# def set_log_dir(self, directory: Path) -> None:
	# 	# TODO: path validation
	# 	self._log_dir = directory

	def log(self, event_level: EventLevel, message: str, channel: EventChannel) -> None:
		with self._io_lock:
			event = EventLog(event_level, message)

			ctx = _LOG_CONTEXT.get()
			if ctx:
				event.metadata.update(ctx)

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

				# e.destination = ctx.get('destination', "UNKNOWN")

			# if destination == 'file':
			# 	handler.emit(e)
			# else:
			# for d in destination:
			# 	match d:
			# 		case 'file':
			# 			# self._file_handler.set_directory(self._log_dir)
			# 		case 'console':
