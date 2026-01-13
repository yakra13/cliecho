"""
"""
import getpass
import json
import readline
import socket
import sys
import threading

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import Dict, Final, List, Optional

# from shared.module_base import ModuleBase

from .log_types import EventLog, LogLevel, EventChannel
from .module_context import ModuleContext

# Context-local variables. Each module thread gets its own. Allows the logger to access the events
# and module context data belonging to its specific module thread
_CURRENT_EVENT_QUEUE: ContextVar[Optional[Queue]]           = ContextVar("current_queue", default=None)
_CURRENT_MODULE_CONTEXT: ContextVar[Optional[ModuleContext]] = ContextVar("module_context", default=None)

@contextmanager
def module_event_queue(queue: Optional[Queue]):
    token = _CURRENT_EVENT_QUEUE.set(queue)
    try:
        yield
    finally:
        _CURRENT_EVENT_QUEUE.reset(token)

@contextmanager
def module_logging_context(context: ModuleContext):
    token = _CURRENT_MODULE_CONTEXT.set(context)
    try:
        yield
    finally:
        _CURRENT_MODULE_CONTEXT.reset(token)

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
    LogLevel.WARN: Color.FG.YELLOW,
    LogLevel.INFO: Color.FG.DEFAULT,
    LogLevel.DEBUG: Color.FG.CYAN,
}


class _ModuleLogger:
    # Gather username and hostname for use in logs
    _username: str = getpass.getuser()
    _hostname: str = socket.gethostname()

    def __init__(self):
        self._io_lock: threading.Lock = threading.Lock()
        self._log_path: Path = Path.home() / "RE/logs"

        if not self._log_path.exists():
            try:
                self._log_path.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise RuntimeError(f"Cannot create log directory '{self._log_path}': {e}") from e
            except OSError as e:
                raise RuntimeError(f"Error creating log directory '{self._log_path}': {e}") from e

    def _format_timestamp(self, timestamp: datetime) -> str:
        return timestamp.strftime("%Y-%m-%d %H:%M:%S") #TODO this is .isoformat()

    def _format_console_output(self, event: EventLog) -> str:
        # TODO
        # ts LogLevel ModuleName Message
        ts = Color.STYLE.DIM + event.timestamp.isoformat()
        
        output: str = ''
        output += Color.STYLE.DIM
        output += event.timestamp.isoformat()
        output += f"{event.module_name}"
        return ''

    def _prepare_event_data(self, event: EventLog) -> None:
        """Populates event data with username, hostname, module settings."""
        if event.username is None:
            event.username = self._username

        if event.hostname is None:
            event.hostname = self._hostname

        if module_context := _CURRENT_MODULE_CONTEXT.get():
            event.module_name = module_context.name
            event.module_options = module_context.options



        # TODO: custom formatting option instead of static?
        # ts = Color.STYLE.DIM + self._format_timestamp(event.timestamp)

        # module = '{' + (event.module_name or 'unknown') + '}' + Color.RESET

        # message = "{}[{}] {}{}".format(LOG_STYLE.get(event.log_level, Color.FG.DEFAULT),
        #                                   event.log_level.name,
        #                                   event.message,
        #                                   Color.RESET)

        # event.formatted_message = f"{ts} {module} {message}"

    def _emit_event(self, event: EventLog) -> None:
        """Emit event on their associated channel"""
        # self._prepare_console_event_data(event)
        # TODO: determine dest file
        # This function should only handle these log levels

        # if event.channel == EventChannel.CONSOLE:
        #     if __debug__:
        #         raise ValueError(f"Attempt to log console message to log file: {event}")

        #     e = EventLog(log_level=LogLevel.ERROR,
        #                  channel=EventChannel.LOG,
        #                  message="Internal logging misuse: console-only log bound to file log",
        #                  metadata={"original_level": event.log_level.name,
        #                            "original_message": event.message,
        #                            "original_timestamp": event.timestamp
        #                            })
        #     event = e
                
        self._prepare_event_data(event)

        # If an event queue is present let the core handle logging
        if event_queue := _CURRENT_EVENT_QUEUE.get():
            event_queue.put(event)
            return

        # Execution is standalone; handle write immediately
        if event.channel == EventChannel.LOG:
            # write to file
            # TODO: determine path, standalone execution need to log to some common
            # per module path. Perhaps ~/.redecho/logs/module_name/*.log
            # And the redcho prime log: ~/.redecho/logs/redecho.log
            # ~/.re/logs
            # /var/logs/re
            # %LOCALAPPDATA%\RE\logs
            module_name: str = event.module_name or "unknown_module"
            log_path: Path = self._log_path / module_name
            log_file: Path = log_path / f"{module_name}.log"

            if not log_path.exists():
                try:
                    log_path.mkdir(parents=True, exist_ok=True)
                except PermissionError as e:
                    raise RuntimeError(f"Cannot create log directory '{log_path}': {e}") from e
                except OSError as e:
                    raise RuntimeError(f"Error creating log directory '{log_path}': {e}") from e
            
            with open(log_file, "a", encoding="utf-8") as file:
                json.dump(event.to_dict(), file)
                file.write("\n")

        elif event.channel == EventChannel.CONSOLE:
            # write to stdout
            sys.stdout.write(self._format_console_output(event))
            sys.stdout.flush()
        else:
            raise NotImplementedError(f"Call to write unimplemented log channel: {event.channel.name}")


    # def _console_write(self, event: EventLog) -> None:
    #     """Handles writes to console."""
    #     # Prepare the message with appropriate log level formatting
    #     self._prepare_event_data(event)

    #     if event_queue := _CURRENT_EVENT_QUEUE.get():
    #         event_queue.put(event)
    #     else:
    #         # No event queue so we log to console immediately
    #         sys.stdout.write(event.message)
    #         sys.stdout.flush()

    #     # self.print_event.clear()
    #     with self._io_lock:
    #         print(f'{ts} {module} {message}')
    #     # self.print_event.set()

    def log_info(self, message: str) -> None:
        """Log info event to file"""
        event = EventLog(log_level=LogLevel.INFO, channel=EventChannel.LOG, message=message)
        self._emit_event(event)

    def log_warn(self, message: str) -> None:
        """Log warning event to file"""
        event = EventLog(log_level=LogLevel.WARN, channel=EventChannel.LOG, message=message)
        self._emit_event(event)

    def log_error(self, message: str) -> None:
        """Log error event to file"""
        event = EventLog(log_level=LogLevel.ERROR, channel=EventChannel.LOG, message=message)
        self._emit_event(event)

    def console_raw(self, message:str) -> None:
        """Log unformatted message to console"""
        event = EventLog(log_level=LogLevel.RAW, channel=EventChannel.CONSOLE, message=message)
        self._emit_event(event)
        
    def console_info(self, message:str) -> None:
        """Log formatted info event to console"""
        event = EventLog(log_level=LogLevel.INFO, channel=EventChannel.CONSOLE, message=message)
        self._emit_event(event)

    def console_warn(self, message: str) -> None:
        """Log formatted warning event to console"""
        event = EventLog(log_level=LogLevel.WARN, channel=EventChannel.CONSOLE, message=message)
        self._emit_event(event)

    def console_error(self, message: str) -> None:
        """Log formatted error event to console"""
        event = EventLog(log_level=LogLevel.ERROR, channel=EventChannel.CONSOLE, message=message)
        self._emit_event(event)

LOGGER = _ModuleLogger()
