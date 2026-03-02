
import socket
from abc import ABC, abstractmethod

# TLS
# import ssl

# ssl_sock = ssl_context.wrap_socket(sock, server_side=True)
# transport = TCPTransport(ssl_sock, addr)

class Transport(ABC):
	@abstractmethod
	def read(self, size: int = 4096) -> bytes:
		...

	@abstractmethod
	def write(self, data: bytes) -> None:
		...

	@abstractmethod
	def close(self) -> None:
		...

	@abstractmethod
	def is_alive(self) -> bool:
		...

class TCPTransport(Transport):
	def __init__(self, sock: socket.socket, addr):
		self._sock = sock
		self._addr = addr
		self._sock.setblocking(True)
		self._is_alive = True

	@property
	def peer(self):
		return self._addr

	def read(self, size: int = 4096) -> None:
		try:
			data = self._sock.recv(size)
			if not data:
				self._is_alive = False
			return data
		except OSError:
			self._is_alive = False
			return b""

	def write(self, data: bytes) -> None:
		if not self._alive:
			return
		
		try:
			self.sock.sendall(data)
		except OSError:
			self._is_alive = False

	def close(self):
		self._is_alive = False
		try:
			self._sock.close()
		except OSError:
			pass

	def is_alive(self):
		return self.is_alive()

class BufferedTransport(TCPTransport):

    def __init__(self, sock, addr):
        super().__init__(sock, addr)
        self.buffer = bytearray()

    def read_until(self, delimiter: bytes):
        while delimiter not in self.buffer:
            self.buffer.extend(super().read())

        idx = self.buffer.index(delimiter)
        result = self.buffer[:idx]
        self.buffer = self.buffer[idx+len(delimiter):]
        return bytes(result)