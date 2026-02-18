from typing import Dict, Final, List, Optional
from logger.formatter import Formatter
from logger.log_event import EventLevel, EventLog
from formatter import style_text
from color import Color

class ConsoleLevelFormatter(Formatter):
	"""Colorize event message based on event level."""
	_DEFAULT_PALETTE: Final[List[Color]] = [
		Color.White,  # INFO
		Color.Yellow, # WARN
		Color.Red, 	  # ERROR
		Color.Teal 	  # DEBUG
	]

	def __init__(self, palette: Optional[List[Color]] = None):
		self.palette: List[Color] = palette or self._DEFAULT_PALETTE

	def format(self, event: EventLog) -> str:
		index = event.level.value - 1
		# color = self.palette.get(event.event_level, Color.White)
		if 0 <= index < len(self.palette):
			color = self.palette[index]
		else:
			color = Color.White

		return style_text(event.message, color)
