
from abc import ABC, abstractmethod
from enum import Enum, auto
import socket
import threading

class ListenerState(Enum):
	STOPPED = auto()
	STARTING = auto()
	RUNNING = auto()
	STOPPING = auto()

class Listener(ABC):
	def __init__(self, host: str, port: int):
		self.host = host
		self.port = port
		self.is_running = False

	@abstractmethod
	def start(self) -> None:
		...

	@abstractmethod
	def stop(self) -> None:
		...


class TCPListener(Listener):
	def start(self):
		self.is_running = True
		self._thread = threading.Thread(target=self._run, daemon=True)
		self._thread.start()

	def stop(self):
		self.is_running = False
		self._sock.close()

	def _run(self):
		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.bind(self.host, self.port)
		self._socket.listen()

		while self.is_running:
			conn, addr = self._sock.accept()

			transport = TCPTransport(conn, addr)

			if self.on_connection:
				self.on_connection(transport)

class ListenerManager:
	def __init__(self):
		self.listeners = {}

	def add(self, name: str, listener: Listener):
		self.listeners[name] = listener
		listener.start()

	def stop(self, name: str):
		self.listeners[name].stop()
