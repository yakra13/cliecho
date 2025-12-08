"""
"""
import getpass
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Optional, Any

class LogLevel(Enum):
    """
    Docstring for LogLevel
    """
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    # TODO: Special Log levels

@dataclass
class Event:
    """
    Docstring for Event
    """
    log_level: LogLevel
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    username: str = field(default_factory=getpass.getuser)
    hostname: str = field(default_factory=socket.gethostname)

    module_name: Optional[str] = None
    module_options: dict[str, Any] = field(default_factory=dict)
