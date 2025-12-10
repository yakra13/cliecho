"""
"""
import getpass
import socket
from contextlib import contextmanager
from contextvars import ContextVar
# from dataclasses import replace
from queue import Queue
from typing import Optional

from .log_types import Event, LogLevel
from .module_context import ModuleContext

_current_queue: ContextVar[Optional[Queue]] = ContextVar("current_queue", default=None)
_module_context: ContextVar[Optional[ModuleContext]] = ContextVar("module_context", default=None)

# TODO: can get rid of these two functions and just call the set() in the contextmanagers below
# def _set_event_queue(queue: Optional[Queue]) -> None:
#     """
#     Docstring for set_event_queue
    
#     :param queue: Description
#     :type queue: Optional[Queue]
#     """
#     _current_queue.set(queue)

# def _set_module_context(context: Optional[ModuleContext]) -> None:
#     """
#     Docstring for set_module_context
    
#     :param context: Description
#     :type context: Optional[ModuleContext]
#     """
#     _module_context.set(context)

# def get_event_queue() -> Optional[Queue]:
#     return _event_queue.get()

@contextmanager
def module_event_queue(queue: Optional[Queue]):
    """
    Docstring for module_event_queue
    
    :param queue: Description
    :type queue: Optional[Queue]
    """
    # _set_event_queue(queue)
    _current_queue.set(queue)
    try:
        yield
    finally:
        _current_queue.set(None)

@contextmanager
def module_logging_context(context: ModuleContext):
    """
    Docstring for module_logging_context
    
    :param context: Description
    :type context: ModuleContext
    """
    # _set_module_context(context)
    _module_context.set(context)
    try:
        yield
    finally:
        _module_context.set(None)

class _ModuleLogger:
    _username: str = getpass.getuser()
    _hostname: str = socket.gethostname()

    def _prepare_event_data(self, event) -> None:

        if event.username is None:
            event.username = self._username

        if event.hostname is None:
            event.hostname = self._hostname

        if module_context := _module_context.get():
            event.module_name = module_context.name
            event.module_options = module_context.options

    def _write(self, event: Event) -> None:
        self._prepare_event_data(event)

        if event_queue := _current_queue.get():
            event_queue.put(event)
        else:
            # Standalone logging
            # TODO
            pass

    def _console_write(self, event: Event) -> None:
        self._prepare_event_data(event)

        # TODO: print to terminal with formatting

    def log_info(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        self._write(Event(log_level=LogLevel.INFO, message=message))

    def log_warn(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        self._write(Event(log_level=LogLevel.WARNING, message=message))

    def log_error(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        self._write(Event(log_level=LogLevel.ERROR, message=message))

    def console_info(self, message:str) -> None:
        """
        Docstring for console_info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        self._console_write(Event(log_level=LogLevel.INFO, message=message))

    def console_warn(self, message: str) -> None:
        """
        Docstring for console_warn
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        self._console_write(Event(log_level=LogLevel.WARNING, message=message))

    def console_error(self, message: str) -> None:
        """
        Docstring for console_error
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        self._console_write(Event(log_level=LogLevel.ERROR, message=message))

LOGGER = _ModuleLogger()
