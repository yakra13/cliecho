"""
"""
# TODO: this was all moved into module_logger
# from dataclasses import dataclass, field, asdict
# from datetime import datetime, timezone
# from enum import Enum, auto
# from typing import Optional, Any, Dict

# from shared.color import Color
# from shared.formatter import format_timestamp_epoch
# from shared.util import get_system_hostname, get_system_username

# class EventLevel(Enum):
#     """Defines the log level of events"""
#     INFO  = auto()
#     WARN  = auto()
#     ERROR = auto()
#     DEBUG = auto()
#     RAW   = auto()
#     # TODO: Special Log levels?
#     @property
#     def color(self) -> Optional[Color]:
#         mapping = {
#             EventLevel.INFO: Color.White,
#             EventLevel.WARN: Color.Yellow,
#             EventLevel.ERROR: Color.Red,
#             EventLevel.DEBUG: Color.Cyan,
#             EventLevel.RAW: None
#         }

#         return mapping.get(self, None)

# class EventChannel(Enum):
#     """Defines channels that events emit on"""
#     CONSOLE = auto() # stdout
#     LOG     = auto() # to file

# @dataclass
# class EventLog:
#     """Dataclass containing event log information"""
#     event_level: EventLevel
#     event_channel: EventChannel
#     message: str
#     timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc)) # TODO: standardize/globalize timezone
#     username: Optional[str] = None # = field(default_factory=getpass.getuser)
#     hostname: Optional[str] = None # = field(default_factory=socket.gethostname)

#     module_name: Optional[str] = None
#     module_options: Dict[str, Any] = field(default_factory=dict)
#     metadata: Dict[str, Any] = field(default_factory=dict)

#     def __post_init__(self):
#         self.username = get_system_username()
#         self.hostname = get_system_hostname()

#     def to_dict(self) -> Dict[str, Any]:
#         """Converts this event into a dictionary format."""
#         d = asdict(self)

#         d["timestamp"]     = format_timestamp_epoch(self.timestamp)
#         d["event_level"]   = self.event_level.name
#         d["event_channel"] = self.event_channel.name

#         return d
