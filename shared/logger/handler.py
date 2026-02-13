from pathlib import Path
import sys
from typing import Callable, Dict, TextIO

from formatter import Formatter
from log_event import EventLog

class Handler:
	def __init__(self, formatter: Formatter):
		self._formatter = formatter

	def emit(self, event: EventLog) -> None:
		pass


class FileHandler(Handler):
	def __init__(self, formatter: Formatter, directory: Path): #, router: Callable[[object], Path]):
		self._formatter: Formatter = formatter
		self._directory: Path = directory
		# self._router: Callable[[object], Path] = router
		self._files: Dict[str, TextIO] = {}
		self._is_closed: bool = False

	def _get_file(self, event: EventLog) -> TextIO:
		file_name: str = event.metadata.get('destination', None) or "SOME_DEFAULT.log" # possibly a hash or something 
		full_path: Path = self._directory / file_name

		full_path.parent.mkdir(parents=True, exist_ok=True)
		if file_name not in self._files:
			self._files[file_name] = open(full_path, 'a', encoding='utf-8')
		
		return self._files[file_name]

	def emit(self, event: EventLog) -> None:
		if self._is_closed:
			raise RuntimeError("FileHandler is closed.")

		file = self._get_file(event)

		message = self._formatter.format(event)

		file.write(message + '\n')
		file.flush()

	def close(self) -> None:
		if self._is_closed:
			return

		for f in self._files.values():
			try:
				f.close()
			except:
				pass # TODO: optional logging fallback?
		
		self._files.clear()
		self._is_closed = True



class StreamHandler(Handler):
	def emit(self, event: EventLog):
		sys.stdout.write(self._formatter.format(event))
		sys.stdout.flush()

class ContextFileHandler(Handler):
	def __init__(self, base_dir: Path, formatter: Formatter):
		self._base_dir = base_dir
		self._formatter = formatter

	def _get_file(self, event: EventLog)

	def emit(self, event: EventLog):