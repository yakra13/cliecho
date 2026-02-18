from functools import cache
import getpass
# import ipaddress
import os
import socket
import sys
import platform
# from typing import Final, List

import psutil

class SystemInfo:
    @staticmethod
    @cache
    def get_system_total_ram() -> int:
        """Gets total system RAM in bytes and caches the result."""
        return psutil.virtual_memory().total

    @staticmethod
    def get_app_ram_usage() -> int:
        process = psutil.Process(os.getpid())
        # rss is the physical memory currently used by this process
        mem_bytes = process.memory_info().rss

        return mem_bytes

    @staticmethod
    @cache
    def get_system_os() -> str:
        """Gets the OS and caches the result."""
        return sys.platform

    @staticmethod
    @cache
    def get_system_architecture() -> str:
        """Gets the system architecture 'x86_64 or 'arm64' and caches the result."""
        arch = platform.machine()
        if not arch:
            arch = platform.processor()
        return arch or "unknown"

    @staticmethod
    @cache
    def get_system_max_threads() -> int:
        """Calculates system thread capacity once and caches the result."""
        try:
            return len(os.sched_getaffinity(0))
        except AttributeError:
            return os.cpu_count() or 1

    @staticmethod
    @cache
    def get_system_username() -> str:
        """Gets the current username once and caches the result."""
        return getpass.getuser()

    @staticmethod
    @cache
    def get_system_hostname() -> str:
        """Gets the hostname once and caches the result."""
        return socket.gethostname()

    @staticmethod
    @cache
    def get_local_ip() -> str:
        """Gets the primary local IP address and caches the result."""
        try:
            # Does not actually connect but finds the interface for the 'internet'
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("1.1.1.1",80))
                return sock.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    @staticmethod
    @cache
    def get_fqdn() -> str:
        """Gets the Fully Qualified Domain Name and caches the result."""
        return socket.getfqdn()