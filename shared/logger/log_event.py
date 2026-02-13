from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, Optional

# _LOG_CONTEXT: ContextVar[Dict[str, Any]] = ContextVar("log_context", default={})

# @contextmanager
# def logging_context(**values: Any):
#     current = _LOG_CONTEXT.get()
#     new_context = {**current, **values}

#     token = _LOG_CONTEXT.set(new_context)
#     try:
#         yield
#     finally:
#         _LOG_CONTEXT.reset(token)


class EventLevel(Enum):
    """Defines the log level of events"""
    INFO  = auto()
    WARN  = auto()
    ERROR = auto()
    DEBUG = auto()
    RAW   = auto()
    # TODO: Special Log levels?
    # @property
    # def color(self) -> Optional[Color]:
    #     mapping = {
    #         EventLevel.INFO: Color.White,
    #         EventLevel.WARN: Color.Yellow,
    #         EventLevel.ERROR: Color.Red,
    #         EventLevel.DEBUG: Color.Cyan,
    #         EventLevel.RAW: None
    #     }

    #     return mapping.get(self, None)

@dataclass
class EventLog:
    """Dataclass containing event log information"""
    event_level: EventLevel
    # event_channel: EventChannel
    message: str
    # destination: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc)) # TODO: standardize/globalize timezone
    # username: Optional[str] = None # = field(default_factory=getpass.getuser)
    # hostname: Optional[str] = None # = field(default_factory=socket.gethostname)

    # module_name: Optional[str] = None
    # module_options: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # def __post_init__(self):
    #     # self.username = self.username or SystemInfo.get_system_username()
    #     # self.hostname = self.hostname or SystemInfo.get_system_hostname()

    #     # if (ctx := _CURRENT_MODULE_CONTEXT.get()):
    #     #     self.module_name = self.module_name or ctx.name
    #     #     self.module_options = self.module_options or ctx.options

    #     ctx = _LOG_CONTEXT.get()
    #     if ctx:
    #         self.metadata.update(ctx)

    def to_dict(self) -> Dict[str, Any]:
        """Converts this event into a dictionary format."""
        d = asdict(self)

        d["timestamp"]     = self.timestamp#format_timestamp_epoch(self.timestamp)
        d["event_level"]   = self.event_level.name
        # d["event_channel"] = self.event_channel.name

        return d