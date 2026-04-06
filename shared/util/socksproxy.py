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