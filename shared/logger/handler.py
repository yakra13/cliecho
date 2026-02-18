import sys
import threading
from pathlib import Path
from queue import Queue
from typing import Literal, Optional, TextIO

from .formatter import Formatter
from .log_event import EventLog

class Handler:
	def __init__(self, formatter: Formatter):
		self._lock: threading.Lock = threading.Lock()
		self._formatter: Formatter = formatter

	def emit(self, event: EventLog) -> None:
		raise NotImplementedError

	def close(self) -> None:
		raise NotImplementedError

class QueueHandler(Handler):
	def __init__(self, formatter: Formatter, queue: Queue):
		super().__init__(formatter)
		self.queue = queue

	def emit(self, event: EventLog) -> None:
		formatted_data = self._formatter.format(event)
		self.queue.put(formatted_data)

	def close(self) -> None:
		return

class StreamHandler(Handler):
	def __init__(self, formatter: Formatter):
		super().__init__(formatter)
		self._is_closed: bool = False
		self._stream: Optional[TextIO] = None

	def emit(self, event: EventLog) -> None:
		formatted_data = self._formatter.format(event)

		with self._lock:
			if self._is_closed:
				raise RuntimeError("Handler is closed.")

			if self._stream is None:
				raise RuntimeError("Stream is none")

			self._stream.write(formatted_data)
			self._stream.flush()

	def close(self) -> None:
		with self._lock:
			if self._is_closed:
				return
			
			if self._stream:
				self._stream.flush()
				self._stream.close()

			self._is_closed = True

class FileHandler(StreamHandler):
	def __init__(self, formatter: Formatter, path: Path):
		super().__init__(formatter)
		self._path: Path = path
		self._stream = open(self._path, 'a', encoding='utf-8')

class ConsoleHandler(StreamHandler):
	def __init__(self, formatter: Formatter, stream: Literal['stdout', 'stderr'] = 'stdout'):
		super().__init__(formatter)
		self._stream = sys.stderr if stream == 'stderr' else sys.stdout

	def close(self) -> None:
		with self._lock:
			if self._is_closed:
				return
			
			if self._stream:
				self._stream.flush()

			self._is_closed = True
