"""
TODO: file oc string
"""
from enum import Enum, auto


class SessionState(Enum):
	"""
	TODO: this doc string
	"""
	BACKGROUND = auto()
	FOREGROUND = auto()
	CLOSED = auto()

class Session:
	id: str
	transport: Transport
	adapter
	state: SessionState