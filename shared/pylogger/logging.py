from collections.abc import Mapping
from contextlib import contextmanager
from dataclasses import is_dataclass
import logging
from logging import LogRecord
from datetime import datetime
from contextvars import Context, ContextVar
from queue import Queue
from typing import Any



# class Formatter(logging.Formatter):
# 	def format(self, record: LogRecord):
# 		record.
_EVENT_QUEUE: ContextVar[Queue | None] = ContextVar("event_queue", default=None)
_log_context: ContextVar[dict[str, Any]] = ContextVar("log_context", default={})

def normalize_context(context: Context) -> dict:
    if context is None:
        return {}
    
    if is_dataclass(context):
        return asdict(context)

    if isinstance(context, Mapping):
        return dict(context)

    # Fallback
    return vars(context)


@contextmanager
def event_queue(queue: Queue):
	token = _EVENT_QUEUE.set(queue)

	try:
		yield
	finally:
		_EVENT_QUEUE.reset(token)

@contextmanager
def logging_context(context: dict, **kwargs: Any):
	current = _log_context.get()

	merged = {**current}

	if context:
		merged.update(normalize_context(context))
	# new_context = {**current, **kwargs}	

	merged.update(kwargs)
	
	token = _log_context.set(merged)

	try:
		yield
	finally:
		ctx_id = merged.get("id", "default")
		Logger._close_context(ctx_id)
		_log_context.reset(token)
