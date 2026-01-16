"""
"""
from enum import Enum
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
from typing import Dict, Final, Iterable, List, Literal, Optional


# from shared.module_base import ModuleBase

from shared.ansi import AnsiStyle
from shared.log_types import EventLog, LogLevel, EventChannel
from shared.module_context import ModuleContext
from shared.color import Color
from shared.formatter import style_text #Color, FGColor, color_text

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


class _ModuleLogger:
    # Gather username and hostname for use in logs
    _username: str = getpass.getuser()
    _hostname: str = socket.gethostname()

    def __init__(self):
        self._io_lock: threading.Lock = threading.Lock()
        self._log_path: Path = Path.home() / "RE/logs" #TODO where we puttin stuff?

        if not self._log_path.exists():
            try:
                self._log_path.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise RuntimeError(f"Cannot create log directory '{self._log_path}': {e}") from e
            except OSError as e:
                raise RuntimeError(f"Error creating log directory '{self._log_path}': {e}") from e

    def _format_console_output(self, event: EventLog) -> str:
        # TODO: defined colorization options from config file?
        if event.log_level == LogLevel.RAW:
            return event.message

        log_level_color: Optional[Color] = None

        match event.log_level:
            case LogLevel.ERROR:
                log_level_color = Color.Red
            case LogLevel.WARN:
                log_level_color = Color.Yellow
            case LogLevel.DEBUG:
                log_level_color = Color.Cyan

        timestamp = style_text(text=event.timestamp.isoformat(),
                               styles=[AnsiStyle.DIM])

        module = style_text(text=f"[{(event.module_name or 'unknown')}]",
                            text_color=Color.Black,
                            back_color=Color.DarkGray,
                            styles=[AnsiStyle.DIM])
        
        level = style_text(text=event.log_level.name,
                           text_color=log_level_color,
                           styles=[AnsiStyle.BOLD])
        
        return f"{timestamp} {module} {level} {event.message}"

    def _prepare_event_data(self, event: EventLog) -> None:
        """Populates event data with username, hostname, module settings."""
        if event.username is None:
            event.username = self._username

        if event.hostname is None:
            event.hostname = self._hostname

        if module_context := _CURRENT_MODULE_CONTEXT.get():
            event.module_name = module_context.name
            event.module_options = module_context.options

    def _emit_event(self, event: EventLog) -> None:
        """Emit event on their associated channel"""       
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

    def log_info(self, message: str) -> None:
        """Log info event to file"""
        event = EventLog(log_level=LogLevel.INFO,
                         channel=EventChannel.LOG,
                         message=message)
        self._emit_event(event)

    def log_warn(self, message: str) -> None:
        """Log warning event to file"""
        event = EventLog(log_level=LogLevel.WARN,
                         channel=EventChannel.LOG,
                         message=message)
        self._emit_event(event)

    def log_error(self, message: str) -> None:
        """Log error event to file"""
        event = EventLog(log_level=LogLevel.ERROR,
                         channel=EventChannel.LOG,
                         message=message)
        self._emit_event(event)

    def console_raw(self, message:str) -> None:
        """Log unformatted message to console"""
        event = EventLog(log_level=LogLevel.RAW,
                         channel=EventChannel.CONSOLE,
                         message=message)
        self._emit_event(event)
        
    def console_info(self, message:str) -> None:
        """Log formatted info event to console"""
        event = EventLog(log_level=LogLevel.INFO,
                         channel=EventChannel.CONSOLE,
                         message=message)
        self._emit_event(event)

    def console_warn(self, message: str) -> None:
        """Log formatted warning event to console"""
        event = EventLog(log_level=LogLevel.WARN,
                         channel=EventChannel.CONSOLE,
                         message=message)
        self._emit_event(event)

    def console_error(self, message: str) -> None:
        """Log formatted error event to console"""
        event = EventLog(log_level=LogLevel.ERROR,
                         channel=EventChannel.CONSOLE,
                         message=message)
        self._emit_event(event)


LOGGER = _ModuleLogger()
