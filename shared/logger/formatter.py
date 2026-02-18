from enum import IntEnum, auto
from typing import Iterable, Optional
from .log_event import EventLevel, EventLog
from text.ansi import AnsiStyle
from text.color import Color

class Verbosity(IntEnum):
	MINIMAL = auto()
	NORMAL = auto()
	VERBOSE = auto()
	DEBUG = auto()

class Formatter:
	def __init__(self, verbosity: Verbosity = Verbosity.NORMAL):
		self._verbosity = verbosity

	def update_verbosity(self, verbosity: Verbosity) -> None:
		self._verbosity = verbosity

	def format(self, event: EventLog) -> str:
		return '' # TODO

class JsonFormatter(Formatter):
	def format(self, event: EventLog) -> str:
		import json
		return json.dumps(event.to_dict(),
						  separators=(',', ':'),
						  sort_keys=True,
						  indent=4) + '\n'

class ConsoleFormatter(Formatter):
	def format(self, event: EventLog) -> str:
		msg = event.message

		if self._verbosity >= Verbosity.NORMAL:
			msg = f"[{event.level.name}] {msg}"

		if self._verbosity >= Verbosity.VERBOSE:
			msg = f"[{event.metadata.get('name', '-')}] {msg}"

		if self._verbosity >= Verbosity.DEBUG:
			msg = f"{msg}\n\tmetadata={{{event.metadata}}}"

		return msg + '\n'

# TODO: the below is just her for testing
def style_text(text: str,
               text_color: Optional[Color] = None,
               back_color: Optional[Color] = None,
               styles: Optional[Iterable[AnsiStyle]] = None) -> str:
	"""
	Apply ANSI color and text styling to a string.

	If the current terminal does not support the requested formatting,
	the original text is returned unmodified.

	Args:
		text: The text to be styled.
		text_color: Optional foreground color.
		back_color: Optional background color.
		styles: Optional iterable of text styles (e.g. bold, underline).

	Returns:
		The stylized text if supported; otherwise, the original text.

	Raises:
		None

	"""
	# from core.config import CONFIG
	# if SUPPORTED_ANSI == AnsiSupport.NONE or not CONFIG.enable_ansi:
	#     # NOTE: We assume that even styling is not supported (bold, underline, etc)
	#     return text

	codes = []

	if styles:
		codes.extend([s.value for s in styles])

	if text_color:
        # if SUPPORTED_ANSI == AnsiSupport.TRUECOLOR:
		codes.extend(['38', '2', str(text_color.R), str(text_color.G), str(text_color.B)])
        # else:
        #     # If truecolor is not supported we default to ANSI_16 currently
        #     fg = estimate_ansi_color(text_color)
        #     codes.extend([str(fg)])

	if back_color:
		# if SUPPORTED_ANSI == AnsiSupport.TRUECOLOR:
		codes.extend(['48', '2', str(back_color.R), str(back_color.G), str(back_color.B)])
        # else:
        #     # If truecolor is not supported we default to ANSI_16 currently
        #     bg = estimate_ansi_color(back_color, is_background=True)
        #     # Add ten to shift from foreground ansi color to background
        #     bg += 10
        #     codes.extend([str(bg)])

	seq = ';'.join(codes)

	return f"\033[{seq}m{text}\033[0m"

class AnsiConsoleFormatter(Formatter):
	# TODO: this is a custom formatter not part of this class
	# will do ansi detection and formatting of an eventLog
	def format(self, event: EventLog) -> str:
		msg = event.message

		level_color = Color.White

		match event.level:
			case EventLevel.WARN:
				level_color = Color.Yellow
			case EventLevel.ERROR:
				level_color = Color.Red
			case EventLevel.DEBUG:
				level_color = Color.Aqua

		level = style_text(event.level.name, level_color, None, [AnsiStyle.BOLD])

		name = style_text(event.metadata.get('name', '-'), Color.Gray, None, [AnsiStyle.ITALIC])

		meta = style_text("metadata", Color.Aqua) + "={"

		def color_data(data_dict) -> str:
			output: str = ''
			length = len(data_dict)
			for key, value in data_dict.items():
				length -= 1
				k = style_text(key, Color.Gray)
				v = value

				if type(v) is str:
					v = f"'{v}'"
					v = style_text(v, Color(255, 140, 64))

				if type(v) is int or type(v) is float:
					v = style_text(str(v), Color.Blue)

				if type(v) is dict:
					sub_dict = color_data(v)
					v = f"{{{sub_dict}}}"

				output += f"{k}: {v}"

				if length > 0:
					output += ", "

			return output

		meta += color_data(event.metadata)

		meta += "}"

		if self._verbosity >= Verbosity.NORMAL:
			msg = f"[{level}] {msg}"

		if self._verbosity >= Verbosity.VERBOSE:
			msg = f"[{name}] {msg}"

		if self._verbosity >= Verbosity.DEBUG:
			msg = f"┌{msg}\n└─{meta}"

		return msg + '\n'


		# def color_data(dict) -> str:
		# 	for key, value in event.metadata.items():
		# 		k = style_text(key, Color.Teal)
		# 		v = value
		# 		if type(v) is str:
		# 			v = f"'{v}'"
		# 			v = style_text(v, Color.OrangeRed)
		# 		if type(v) is int or type(v) is float:
		# 			v = style_text(str(v), Color.LimeGreen)
		# 		if type(v) is dict:

		# 		meta += f"{k}={v}, "