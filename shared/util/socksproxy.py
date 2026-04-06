import socks # pip install PySocks
import socket

# s = socks.socksocket()
# # cobalt strike -> socks 1080
# teamserver_ip = "10.0.0.5"
# teamserver_socks_port = 1080
# proxy_type = socks.SOCKS4 # maybe socks5
# s.set_proxy(proxy_type, teamserver_ip, teamserver_socks_port, rdns=True) # rdns=True -> resolve dns on beacon side
# # make connection
# s.connect(("example.com", 80))


from dataclasses import dataclass

# TODO: create a dict of proxyConfigs to support multiple socks proxies on teamserver
# need a convenient way to choose which proxy to use per tool/destination

@dataclass
class ProxyConfig:
    enabled: bool
    host: str
    port: int
    proxy_type: str = "socks4"  # or socks5
    rdns: bool = True
    

from contextlib import contextmanager
from contextvars import ContextVar

# thread local proxy config (allows each thread to use or not use proxy)
_proxy_cfg: ContextVar[ProxyConfig | None] = ContextVar("proxy_cfg", default=None)

# this affects only code that uses socket.socket()
# Custom socket
class ProxyAwareSocket(socks.socksocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cfg = _proxy_cfg.get()
        if cfg and cfg.enabled:
            proxy_type = (
                socks.SOCKS5 if cfg.proxy_type.lower() == "socks5"
                else socks.SOCKS4
            )

            self.set_proxy(
                proxy_type,
                cfg.host,
                cfg.port,
                rdns=cfg.rdns
            )


# install at start up must be called before any tool imports socket
# "monkey patches" socket.socket
def install_proxy_socket():
    socket.socket = ProxyAwareSocket

@contextmanager
def proxy_context(cfg: ProxyConfig | None):
    token = _proxy_cfg.set(cfg)
    try:
        yield
    finally:
        _proxy_cfg.reset(token)


# USAGE:
with proxy_context(ProxyConfig(True, "10.0.0.5", 1080)):
    # tool.run
    # now any calls to socket.socket() are replaced with ProxyAwareSocket
    pass

# @contextmanager
# def proxy_context(cfg: ProxyConfig | None):
#     if not cfg or not cfg.enabled:
#         yield
#         return

#     original_socket = socket.socket

#     try:
#         proxy_type = socks.SOCKS5 if cfg.proxy_type == "socks5" else socks.SOCKS4

#         socks.set_default_proxy(
#             proxy_type,
#             cfg.host,
#             cfg.port,
#             rdns=cfg.rdns
#         )

#         socket.socket = socks.socksocket  # 🔥 global patch

#         yield

#     finally:
#         socket.socket = original_socket  # restore


# import socks
# import socket

# def check_socks_proxy(host: str, port: int, timeout: float = 3.0) -> bool:
#     try:
#         s = socks.socksocket()
#         s.set_proxy(socks.SOCKS4, host, port, rdns=True)

#         s.settimeout(timeout)

#         # Try connecting to something simple
#         s.connect(("1.1.1.1", 80))  # or any reliable target

#         s.close()
#         return True

#     except Exception:
#         return False

# def check_proxy_port_only(host: str, port: int, timeout: float = 2.0) -> bool:
#     try:
#         with socket.create_connection((host, port), timeout=timeout):
#             return True
#     except OSError:
#         return False
    
import socket
from contextlib import closing

# check correct port when setting proxy or call before running the tool in the with statement
def check_socks_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """
    Quick sanity check that the host:port is listening for a SOCKS connection.
    Does NOT touch the internal network behind the proxy.
    """
    try:
        with closing(socket.create_connection((host, port), timeout=timeout)):
            return True
    except OSError:
        return False