"""
"""
from enum import Enum, auto
import getpass
import json
import readline
import socket
import sys
import threading

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from queue import Queue
from typing import Any, Dict, Final, Iterable, List, Literal, Optional


# from shared.module_base import ModuleBase

from core.config import CONFIG
from shared.ansi import AnsiStyle
# from shared.log_types import EventLog, EventLevel, EventChannel
from shared.module_context import ModuleContext
from shared.color import Color
from shared.formatter import format_timestamp_console, format_timestamp_epoch, style_text
from shared.util import SystemInfo #get_system_hostname, get_system_username #Color, FGColor, color_text

# Context-local variables. Each module thread gets its own. Allows the logger to access the events
# and module context data belonging to its specific module thread
_CURRENT_EVENT_QUEUE: ContextVar[Optional[Queue]]            = ContextVar("current_queue", default=None)
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


class EventLevel(Enum):
    """Defines the log level of events"""
    INFO  = auto()
    WARN  = auto()
    ERROR = auto()
    DEBUG = auto()
    RAW   = auto()
    # TODO: Special Log levels?
    @property
    def color(self) -> Optional[Color]:
        mapping = {
            EventLevel.INFO: Color.White,
            EventLevel.WARN: Color.Yellow,
            EventLevel.ERROR: Color.Red,
            EventLevel.DEBUG: Color.Cyan,
            EventLevel.RAW: None
        }

        return mapping.get(self, None)


class EventChannel(Enum):
    """Defines channels that events emit on"""
    CONSOLE = auto() # stdout
    LOG     = auto() # to file


@dataclass
class EventLog:
    """Dataclass containing event log information"""
    event_level: EventLevel
    event_channel: EventChannel
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc)) # TODO: standardize/globalize timezone
    username: Optional[str] = None # = field(default_factory=getpass.getuser)
    hostname: Optional[str] = None # = field(default_factory=socket.gethostname)

    module_name: Optional[str] = None
    module_options: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.username = SystemInfo.get_system_username()
        self.hostname = SystemInfo.get_system_hostname()

        if (ctx := _CURRENT_MODULE_CONTEXT.get()):
            self.module_name = self.module_name or ctx.name
            self.module_options = self.module_options or ctx.options

    def to_dict(self) -> Dict[str, Any]:
        """Converts this event into a dictionary format."""
        d = asdict(self)

        d["timestamp"]     = format_timestamp_epoch(self.timestamp)
        d["event_level"]   = self.event_level.name
        d["event_channel"] = self.event_channel.name

        return d


class _ModuleLogger:
    # Gather username and hostname for use in logs
    # _username: str = getpass.getuser()
    # _hostname: str = socket.gethostname()

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
        # Do not format RAW events
        if event.event_level == EventLevel.RAW:
            return event.message

        timestamp = style_text(text=format_timestamp_console(event.timestamp),
                               #event.timestamp.isoformat(),
                               styles=[AnsiStyle.DIM])

        module = style_text(text=f"[{(event.module_name or 'RedEcho')}]",
                            text_color=Color.Black,
                            back_color=Color.DarkGray,
                            styles=[AnsiStyle.DIM])
        
        level = style_text(text=event.event_level.name,
                           text_color=event.event_level.color,
                           styles=[AnsiStyle.BOLD])
        
        return f"{timestamp} {module} {level}: {event.message}"

    # def _format_timestamp(self, timestamp: datetime) -> str:
    #     return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # def _prepare_event_data(self, event: EventLog) -> None:
    #     """Populates event data with username, hostname, module settings."""
    #     if event.username is None:
    #         event.username = self._username

    #     if event.hostname is None:
    #         event.hostname = self._hostname

    #     if module_context := _CURRENT_MODULE_CONTEXT.get():
    #         event.module_name = module_context.name
    #         event.module_options = module_context.options

    def _emit_event(self, event: EventLog) -> None:
        """Emit event on their associated channel"""       
        # TODO: this should be automatic now; test it no idea if it works
        # self._prepare_event_data(event)

        # If an event queue is present let the core handle logging
        if event_queue := _CURRENT_EVENT_QUEUE.get():
            event_queue.put(event)
            return

        # Execution is standalone; handle write immediately
        if event.event_channel == EventChannel.LOG:
            # write to file
            # TODO: determine path, standalone execution need to log to some common
            # per module path. Perhaps ~/.redecho/logs/module_name/*.log
            # And the redcho prime log: ~/.redecho/logs/redecho.log
            # ~/.re/logs
            # /var/logs/re
            # %LOCALAPPDATA%\RE\logs
            module_name: str = event.module_name or "unknown_module"
            log_path: Path = CONFIG.logs_path / module_name
            # event.
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
        elif event.event_channel == EventChannel.CONSOLE:
            # write to stdout
            sys.stdout.write(self._format_console_output(event) + '\n')
            sys.stdout.flush()
        else:
            raise NotImplementedError(f"Call to write unimplemented log channel: {event.event_channel.name}")

    def log_info(self, message: str) -> None:
        """Log info event to file"""
        event = EventLog(event_level=EventLevel.INFO,
                         event_channel=EventChannel.LOG,
                         message=message)
        self._emit_event(event)

    def log_warn(self, message: str) -> None:
        """Log warning event to file"""
        event = EventLog(event_level=EventLevel.WARN,
                         event_channel=EventChannel.LOG,
                         message=message)
        self._emit_event(event)

    def log_error(self, message: str) -> None:
        """Log error event to file"""
        event = EventLog(event_level=EventLevel.ERROR,
                         event_channel=EventChannel.LOG,
                         message=message)
        self._emit_event(event)

    def log_debug(self, message: str) -> None:
        """Log debug event to file"""
        event = EventLog(event_level=EventLevel.DEBUG,
                         event_channel=EventChannel.LOG,
                         message=message)
        self._emit_event(event)

    def console_raw(self, message:str) -> None:
        """Log unformatted message to console"""
        event = EventLog(event_level=EventLevel.RAW,
                         event_channel=EventChannel.CONSOLE,
                         message=message)
        self._emit_event(event)
        
    def console_info(self, message:str) -> None:
        """Log formatted info event to console"""
        event = EventLog(event_level=EventLevel.INFO,
                         event_channel=EventChannel.CONSOLE,
                         message=message)
        self._emit_event(event)

    def console_warn(self, message: str) -> None:
        """Log formatted warning event to console"""
        event = EventLog(event_level=EventLevel.WARN,
                         event_channel=EventChannel.CONSOLE,
                         message=message)
        self._emit_event(event)

    def console_error(self, message: str) -> None:
        """Log formatted error event to console"""
        event = EventLog(event_level=EventLevel.ERROR,
                         event_channel=EventChannel.CONSOLE,
                         message=message)
        self._emit_event(event)

    def console_debug(self, message: str) -> None:
        """Log formatted debug event to console"""
        event = EventLog(event_level=EventLevel.DEBUG,
                         event_channel=EventChannel.CONSOLE,
                         message=message)
        self._emit_event(event)


LOGGER = _ModuleLogger()
