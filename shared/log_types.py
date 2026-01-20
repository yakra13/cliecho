"""
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Optional, Any, Dict

class LogLevel(Enum):
    """Defines the log level of events"""
    INFO  = auto()
    WARN  = auto()
    ERROR = auto()
    DEBUG = auto()
    RAW   = auto()
    # TODO: Special Log levels?

class EventChannel(Enum):
    """Defines channels that events emit on"""
    CONSOLE = auto() # stdout
    LOG = auto() # to file

@dataclass
class EventLog:
    """Dataclass containing event log information"""
    log_level: LogLevel
    channel: EventChannel
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    username: Optional[str] = None # = field(default_factory=getpass.getuser)
    hostname: Optional[str] = None # = field(default_factory=socket.gethostname)

    module_name: Optional[str] = None
    module_options: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Converts this event into a dictionary"""
        d = asdict(self)

        d["timestamp"] = self.timestamp.isoformat()
        d["level"] = self.log_level.name
        d["channel"] = self.channel.name

        return d
