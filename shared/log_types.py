"""
"""
# import getpass
# import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Optional, Any, Dict

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
    username: Optional[str] = None # = field(default_factory=getpass.getuser)
    hostname: Optional[str] = None # = field(default_factory=socket.gethostname)

    module_name: Optional[str] = None
    module_options: Dict[str, Any] = field(default_factory=Dict)
