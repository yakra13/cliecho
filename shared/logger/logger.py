from contextlib import contextmanager
from contextvars import ContextVar
# from dataclasses import asdict, dataclass, field
# from datetime import datetime, timezone
# from enum import Enum, auto
from pathlib import Path
import threading
from typing import Any, Dict, Literal, Optional, Set

from log_event import EventLevel, EventLog
from handler import FileHandler, ConsoleHandler
from context import Context, normalize_context

Destination = Literal["file", "console"]
DestinationCollection = Set[Destination]

_LOG_CONTEXT: ContextVar[Dict[str, Any]] = ContextVar("log_context", default={})

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

# def normalize_context(obj) -> Dict:
#     if obj is None:
#         return {}
    
#     if is_dataclass(obj):
#         return asdict(obj)

#     if isinstance(obj, Mapping):
#         return dict(obj)

#     # Fallback
#     return vars(obj)

class Logger:
	def __init__(self):
		self._io_lock: threading.Lock = threading.Lock()
		# self._log_dir: Path # TODO
		self._file_handler: FileHandler
		self._console_out_handler: ConsoleHandler
		# self._console_err_handler: ConsoleHandler
		self._is_configured: bool = False

	def configure(self, file_handler: FileHandler, console_handler: ConsoleHandler) -> None:
		if self._is_configured:
			raise RuntimeError("Logger already configured")

		self._file_handler = file_handler
		self._console_out_handler = console_handler

		self._is_configured = True

	# def set_log_dir(self, directory: Path) -> None:
	# 	# TODO: path validation
	# 	self._log_dir = directory

	def log(self, event_level: EventLevel, message: str, destinations: DestinationCollection) -> None:
		# context = _LOG_CONTEXT.get()
		ctx = _LOG_CONTEXT.get()
		e = EventLog(event_level, message)

		if ctx:
			e.metadata.update(ctx)
			# e.destination = ctx.get('destination', "UNKNOWN")

		for d in destinations:
			match d:
				case 'file':
					# self._file_handler.set_directory(self._log_dir)
					self._file_handler.emit(e)
				case 'console':
					self._console_out_handler.emit(e)
