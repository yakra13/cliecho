"""
"""
from dataclasses import dataclass
from datetime import datetime
import getpass
import readline
import socket
import sys

from contextlib import contextmanager
from contextvars import ContextVar
from queue import Queue
import threading
from typing import Dict, Final, List, Optional

from shared.module_base import ModuleBase

from .log_types import EventLog, LogLevel
from .module_context import ModuleContext

# Context-local variables. Each module thread gets its own. Allows the logger to access the events
# and module context data belonging to its specific module thread
_current_queue: ContextVar[Optional[Queue]]          = ContextVar("current_queue", default=None)
_module_context: ContextVar[Optional[ModuleContext]] = ContextVar("module_context", default=None)

@contextmanager
def module_event_queue(queue: Optional[Queue]):
    _current_queue.set(queue)
    try:
        yield
    finally:
        _current_queue.set(None)

@contextmanager
def module_logging_context(context: ModuleContext):
    token = _module_context.set(context)
    try:
        yield
    finally:
        _module_context.reset(token)

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

# from abc import ABC, abstractmethod
# class OutputSink(ABC):
#     @abstractmethod
#     def write(self, message: str) -> None:
#         pass
# from threading import Lock
# class BufferedSink(OutputSink):
#     def __init__(self):
#         self._lock = Lock()
#         self._buffer: List[str] = []

#     def write(self, message: str) -> None:
#         with self._lock:
#             self._buffer.append(message)

#     def flush(self) -> List[str]:
#         with self._lock:
#             data = self._buffer[:]
#             self._buffer.clear()
#         return data
# class ImmediateSink(OutputSink):
#     def write(self, message: str) -> None:
#         sys.stdout.write(message)
#         sys.stdout.flush()

class _ModuleLogger:
    _username: str = getpass.getuser()
    _hostname: str = socket.gethostname()

    def __init__(self):
        # self._lock = threading.Lock()
        self._io_lock: threading.Lock = threading.Lock()
        # self.print_event: threading.Event
        self._console_raw_buffer: List[str] = []
        self._buffers: Dict[str, List[str]] = {}
        # self._sinks: Dict[ModuleBase, OutputSink] = {}
        # self._default_sink: OutputSink = ImmediateSink() # fallback
    
    # TODO: possible circular import with ModuleBase may need to "ModuleBase"
    # def register_module(self, module: ModuleBase, sink: OutputSink):
    #     self._sinks[module] = sink

    # def flush_console(self):
    #     """
    #     Docstring for flush_console
        
    #     :param self: Description
    #     """

    #     with self._io_lock:
    #         try:
    #             for message in self._console_raw_buffer:
    #                 sys.stdout.write(message + '\n')
    #             sys.stdout.flush()
    #         finally:
    #             # Empty the message buffer
    #             self._console_raw_buffer.clear()

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
        # self.print_event.clear()
        with self._io_lock:
            print(f'{ts} {module} {message}')
        # self.print_event.set()

    def log_info(self, message: str) -> None:
        """Docstring for info"""
        # with self._lock:
        #     self._write(EventLog(log_level=LogLevel.INFO, message=message))

    def log_warn(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        # with self._lock:
        #     self._write(EventLog(log_level=LogLevel.WARNING, message=message))

    def log_error(self, message: str) -> None:
        """
        Docstring for info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        # with self._lock:
        #     self._write(EventLog(log_level=LogLevel.ERROR, message=message))

    def console_raw(self, message:str, module: ModuleBase | None = None) -> None:
        """Log directly to the console without formatting."""
        print("in console raw")
        # if module is None:
        #     # try to detect caller
        #     import inspect
        #     frame = inspect.currentframe()
        #     caller = frame.f_back # type: ignore
        #     module = caller.f_locals.get("self") # type: ignore
        #     # check if is instance
        #     # if called from a helper function or 
        #     if module not in self._sinks:
        #         sink = self._default_sink
        #     else:
        #         sink = self._sinks[module]
        # else:
        #     sink = self._sinks.get(module, self._default_sink)

        # sink.write(message)
        # return
        # self.print_event.clear()
        with self._io_lock:
            self._console_raw_buffer.append(message)
            # print(message, flush=True)
            # sys.stdout.write('\n')
            # sys.stdout.write(message + '\n')
        # self.print_event.set()


    def console_info(self, message:str) -> None:
        """
        Docstring for console_info
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        # with self._lock:
        #     self._console_write(EventLog(log_level=LogLevel.INFO, message=message))

    def console_warn(self, message: str) -> None:
        """
        Docstring for console_warn
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        # with self._lock:
        #     self._console_write(EventLog(log_level=LogLevel.WARNING, message=message))

    def console_error(self, message: str) -> None:
        """
        Docstring for console_error
        
        :param self: Description
        :param message: Description
        :type message: str
        """
        # with self._lock:
        #     self._console_write(EventLog(log_level=LogLevel.ERROR, message=message))

LOGGER = _ModuleLogger()
