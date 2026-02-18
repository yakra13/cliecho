from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum, Flag, auto
from typing import Any, Dict

class EventChannel(Flag):
	FILE = auto()
	CONSOLE = auto()

class EventLevel(Enum):
    """Defines the log level of events"""
    INFO  = auto()
    WARN  = auto()
    ERROR = auto()
    DEBUG = auto()
    RAW   = auto()

@dataclass
class EventLog:
	"""Dataclass containing event log information"""
	level: EventLevel
	message: str

	# TODO: standardize/globalize timezone
	timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

	metadata: Dict[str, Any] = field(default_factory=dict)

	def merge_metadata(self, *sources: Dict) -> None:
		for s in sources:
			self.metadata.update(s)

	def to_dict(self) -> Dict[str, Any]:
		"""Converts this event into a dictionary format."""
		# TODO: this func
		d = asdict(self)
		
		d["timestamp"]     = int(self.timestamp.timestamp())#format_timestamp_epoch(self.timestamp)
		d["level"]   = self.level.name
		# d["event_channel"] = self.event_channel.name
		
		return d