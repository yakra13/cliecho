"""
"""
from dataclasses import dataclass
from datetime import datetime
import getpass
import socket

from contextlib import contextmanager
from contextvars import ContextVar
from queue import Queue
import threading
from typing import Final, Optional

from .log_types import EventLog, LogLevel
from .module_context import ModuleContext

_current_queue: ContextVar[Optional[Queue]]          = ContextVar("current_queue", default=None)
_module_context: ContextVar[Optional[ModuleContext]] = ContextVar("module_context", default=None)

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

class Color:
    RESET: Final[str]     = "\033[0m"

    class STYLE:
        BOLD: Final[str]      = "\033[1m"
        DIM: Final[str]       = "\033[2m"
        ITALIC: Final[str]    = "\033[3m"
        UNDERLINE: Final[str] = "\033[4m"
        BLINK: Final[str]     = "\033[5m"
        REVERSE: Final[str]   = "\033[7m"
        HIDDEN: Final[str]    = "\033[8m"
        STRIKE: Final[str]    = "\033[9m"

    class FG:
        BLACK: Final[str]   = "\033[30m"
        RED: Final[str]     = "\033[31m"
        GREEN: Final[str]   = "\033[32m"
        YELLOW: Final[str]  = "\033[33m"
        BLUE: Final[str]    = "\033[34m"
        MAGENTA: Final[str] = "\033[35m"
        CYAN: Final[str]    = "\033[36m"
        WHITE: Final[str]   = "\033[37m"
        DEFAULT: Final[str] = "\033[39m"

    class BG:
        BLACK: Final[str]   = "\033[40m"
        RED: Final[str]     = "\033[41m"
        GREEN: Final[str]   = "\033[42m"
        YELLOW: Final[str]  = "\033[43m"
        BLUE: Final[str]    = "\033[44m"
        MAGENTA: Final[str] = "\033[45m"
        CYAN: Final[str]    = "\033[46m"
        WHITE: Final[str]   = "\033[47m"
        DEFAULT: Final[str] = "\033[49m"

LOG_STYLE = {
    LogLevel.ERROR: Color.FG.RED + Color.STYLE.BOLD,
    LogLevel.WARNING: Color.FG.YELLOW,
    LogLevel.INFO: Color.FG.DEFAULT,
    LogLevel.DEBUG: Color.FG.CYAN,
}

class _ModuleLogger:
    _username: str = getpass.getuser()
    _hostname: str = socket.gethostname()

    def __init__(self):
        self._lock = threading.Lock()
        self.io_lock: threading.Lock
        self.print_event: threading.Event

    def _format_timestamp(self, timestamp: datetime) -> str:

        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def _prepare_event_data(self, event: EventLog) -> None:

        if event.username is None:
            event.username = self._username

        if event.hostname is None:
            event.hostname = self._hostname

        if module_context := _module_context.get():
            event.module_name = module_context.name
            event.module_options = module_context.options

    def _write(self, event: EventLog) -> None:
        self._prepare_event_data(event)

        # If an event queue is present let the core handle logging
        if event_queue := _current_queue.get():
            event_queue.put(event)
        else:
            # Standalone logging
            # TODO: write to a per module log
            pass

    def _console_write(self, event: EventLog) -> None:
        self._prepare_event_data(event)

        ts = Color.STYLE.DIM + self._format_timestamp(event.timestamp)

        module = '{' + (event.module_name or 'unknown') + '}' + Color.RESET

        message = "{}[{}] {}{}".format(LOG_STYLE.get(event.log_level, Color.FG.DEFAULT),
                                          event.log_level.name,
                                          event.message,
                                          Color.RESET)
        self.print_event.clear()
        with self.io_lock:
            print(f'{ts} {module} {message}')
        self.print_event.set()

    def log_info(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        with self._lock:
            self._write(EventLog(log_level=LogLevel.INFO, message=message))

    def log_warn(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        with self._lock:
            self._write(EventLog(log_level=LogLevel.WARNING, message=message))

    def log_error(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        with self._lock:
            self._write(EventLog(log_level=LogLevel.ERROR, message=message))

    def console_raw(self, message:str) -> None:
        """Log directly to the console without formatting."""
        self.print_event.clear()
        with self.io_lock:
            print(message)
        self.print_event.set()


    def console_info(self, message:str) -> None:
        """
        Docstring for console_info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        with self._lock:
            self._console_write(EventLog(log_level=LogLevel.INFO, message=message))

    def console_warn(self, message: str) -> None:
        """
        Docstring for console_warn
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        with self._lock:
            self._console_write(EventLog(log_level=LogLevel.WARNING, message=message))

    def console_error(self, message: str) -> None:
        """
        Docstring for console_error
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        with self._lock:
            self._console_write(EventLog(log_level=LogLevel.ERROR, message=message))

LOGGER = _ModuleLogger()
