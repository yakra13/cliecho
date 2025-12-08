"""
"""
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional
from queue import Queue

from log_types import Event, LogLevel
from module_context import ModuleContext

_current_queue: ContextVar[Optional[Queue]] = ContextVar("current_queue", default=None)
_module_context: ContextVar[Optional[ModuleContext]] = ContextVar("module_context", default=None)

# TODO: can get rid of these two functions and just call the set() in the contextmanagers below
def _set_event_queue(queue: Optional[Queue]) -> None:
    """
    Docstring for set_event_queue
    
    :param queue: Description
    :type queue: Optional[Queue]
    """
    _current_queue.set(queue)

def _set_module_context(context: Optional[ModuleContext]) -> None:
    """
    Docstring for set_module_context
    
    :param context: Description
    :type context: Optional[ModuleContext]
    """
    _module_context.set(context)

# def get_event_queue() -> Optional[Queue]:
#     return _event_queue.get()

@contextmanager
def module_event_queue(queue: Optional[Queue]):
    """
    Docstring for module_event_queue
    
    :param queue: Description
    :type queue: Optional[Queue]
    """
    _set_event_queue(queue)
    try:
        yield
    finally:
        _set_event_queue(None)

@contextmanager
def module_logging_context(context: ModuleContext):
    """
    Docstring for module_logging_context
    
    :param context: Description
    :type context: ModuleContext
    """
    _set_module_context(context)
    try:
        yield
    finally:
        _set_module_context(None)

class _ModuleLogger:
    def _write(self, event: Event) -> None:

        if module_context := _module_context.get():
            event.module_name = module_context.name
            event.module_options = module_context.options

        if event_queue := _current_queue.get():
            event_queue.put(event)
        else:
            # Standalone logging
            # TODO
            pass

    def info(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        self._write(Event(log_level=LogLevel.INFO, message=message))

    def warn(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        self._write(Event(log_level=LogLevel.INFO, message=message))

    def error(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        self._write(Event(log_level=LogLevel.INFO, message=message))

LOGGER = _ModuleLogger()
