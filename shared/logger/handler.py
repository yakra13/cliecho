from pathlib import Path
from queue import Queue
import sys
import threading
from typing import Callable, Dict, Literal, Optional, TextIO, Tuple

from formatter import Formatter
from log_event import EventLog

class Handler:
	def __init__(self, formatter: Formatter):
		self._lock: threading.Lock = threading.Lock()
		self._formatter: Formatter = formatter

	def emit(self, event: EventLog) -> None:
		raise NotImplementedError

	def close(self) -> None:
		pass

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

# class FileHandler(IOHandler):
# 	def __init__(self, formatter: Formatter, directory: Path): #, router: Callable[[object], Path]):
# 		# self._formatter: Formatter = formatter
# 		super().__init__(formatter)
# 		self._directory: Path = directory
# 		# self._router: Callable[[object], Path] = router
# 		self._files: Dict[str, TextIO] = {}
# 		self._is_closed: bool = False

# 	def _get_file(self, event: EventLog) -> TextIO:
# 		file_name: str = event.metadata.get('destination', None) or "SOME_DEFAULT.log" # possibly a hash or something 
# 		full_path: Path = self._directory / file_name

# 		full_path.parent.mkdir(parents=True, exist_ok=True)
# 		if file_name not in self._files:
# 			self._files[file_name] = open(full_path, 'a', encoding='utf-8')
		
# 		return self._files[file_name]

# 	def emit(self, event: EventLog) -> None:
# 		if self._is_closed:
# 			raise RuntimeError("FileHandler is closed.")

# 		file = self._get_file(event)

# 		message = self._formatter.format(event)

# 		file.write(message + '\n')
# 		file.flush()

# 	def close(self) -> None:
# 		if self._is_closed:
# 			return

# 		for f in self._files.values():
# 			try:
# 				f.close()
# 			except:
# 				pass # TODO: optional logging fallback?
		
# 		self._files.clear()
# 		self._is_closed = True





# class ContextFileHandler(Handler):
# 	def __init__(self, base_dir: Path, formatter: Formatter):
# 		self._base_dir = base_dir
# 		self._formatter = formatter

# 	def _get_file(self, event: EventLog)

# 	def emit(self, event: EventLog):