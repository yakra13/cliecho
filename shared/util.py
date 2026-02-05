from functools import cache
import getpass
import ipaddress
import os
import socket
import sys
import platform
from typing import Final, List

import psutil

# --- Signed Integers (int) ---
# 8-bit
INT8_MIN: Final[int] = -(1 << 7)                # -128
INT8_MAX: Final[int] = (1 << 7) - 1             # 127
# 16-bit
INT16_MIN: Final[int] = -(1 << 15)              # -32,768
INT16_MAX: Final[int] = (1 << 15) - 1           # 32,767
# 32-bit
INT32_MIN: Final[int] = -(1 << 31)              # -2,147,483,648
INT32_MAX: Final[int] = (1 << 31) - 1           # 2,147,483,647
# 64-bit
INT64_MIN: Final[int] = -(1 << 63)              # -9,223,372,036,854,775,808
INT64_MAX: Final[int] = (1 << 63) - 1           # 9,223,372,036,854,775,807

# --- Unsigned Integers (uint) ---
# 8-bit
UINT8_MIN: Final[int] = 0
UINT8_MAX: Final[int] = (1 << 8) - 1            # 255
# 16-bit
UINT16_MIN: Final[int] = 0
UINT16_MAX: Final[int] = (1 << 16) - 1          # 65,535
# 32-bit
UINT32_MIN: Final[int] = 0
UINT32_MAX: Final[int] = (1 << 32) - 1          # 4,294,967,295
# 64-bit
UINT64_MIN: Final[int] = 0
UINT64_MAX: Final[int] = (1 << 64) - 1          # 18,446,744,073,709,551,615

# --- Unsigned Masks ---
MASK_UINT8:  Final[int] = 0xFF                         # 8-bit mask
MASK_UINT16: Final[int] = 0xFFFF                       # 16-bit mask
MASK_UINT32: Final[int] = 0xFFFFFFFF                   # 32-bit mask
MASK_UINT64: Final[int] = 0xFFFFFFFFFFFFFFFF           # 64-bit mask


# MAX_INT8:  Final[int] = 2**(8 - 1) - 1
# MAX_INT16: Final[int] = 2**(16 - 1) - 1
# MAX_INT32: Final[int] = 2**(32 - 1) - 1
# MAX_INT64: Final[int] = 2**(64 - 1) - 1

# MAX_UINT8:  Final[int] = 2**8 - 1
# MAX_UINT16: Final[int] = 2**16 - 1
# MAX_UINT32: Final[int] = 2**32 - 1
# MAX_UINT64: Final[int] = 2**64 - 1

# MIN_INT8:  Final[int] = -2**(8 - 1)
# MIN_INT16: Final[int] = -2**(16 - 1)
# MIN_INT32: Final[int] = -2**(32 - 1)
# MIN_INT64: Final[int] = -2**(64 - 1)

# MIN_UINT8:  Final[int] = 0
# MIN_UINT16: Final[int] = 0
# MIN_UINT32: Final[int] = 0
# MIN_UINT64: Final[int] = 0

# def clamp_int8(value: int) -> int:
#     return max(MIN_INT8, min(MAX_INT8, int(value)))

# def clamp_int16(value: int) -> int:
#     return max(MIN_INT16, min(MAX_INT16, int(value)))

# def clamp_int32(value: int) -> int:
#     return max(MIN_INT32, min(MAX_INT32, int(value)))

# def clamp_int64(value: int) -> int:
#     return max(MIN_INT64, min(MAX_INT64, int(value)))

# def clamp_uint8(value: int) -> int:
#     return max(MIN_UINT8, min(MAX_UINT8, int(value)))

# def clamp_uint16(value: int) -> int:
#     return max(MIN_UINT16, min(MAX_UINT16, int(value)))

# def clamp_uint32(value: int) -> int:
#     return max(MIN_UINT32, min(MAX_UINT32, int(value)))

# def clamp_uint64(value: int) -> int:
#     return max(MIN_UINT64, min(MAX_UINT64, int(value)))

def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, int(value)))

def lerp(a: float, b: float, t: float) -> float:
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t

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

import re

IP_PATTERN = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){3})(?:\/(\d{1,2})|\-(\d{1,3}))?$')

def parse_ips(addresses: str, split_cidr: bool = False) -> List[str]:
    # 192.168.0.2-10, 192.168.1.0/24, 192.168.2.2
    # split on commas
    unique_entries = []

    cidrs = set()
    individuals = set()

    parts = [p.strip() for p in addresses.split(',')]

    for part in parts:
        match = IP_PATTERN.match(part)
        if not match:
            # TODO: invalid formatting
            continue

        base_ip, cidr_bits, range_end = match.groups()

        # Handle IPs in CIDR notation
        if cidr_bits:
            try:
                net = ipaddress.ip_network(part, strict=False)
                # If the user specified to split CIDR get each ip address
                if split_cidr:
                    for ip in [cidr for cidr in net]:
                        individuals.add(ip)
                else:
                    cidrs.add(str(net))
            except ValueError:
                #TODO: invalid CIDR?
                continue
    
        elif range_end:
            # prefix, start_octet = base_ip.rsplit('.', 1)
            # start_num, end_num = int(start_val), int(range_end)
            prefix, hosts = base_ip.rsplit('.', 1)
            l, r = hosts.split('-', 1)
            beg = int(l)
            end = int(r)
        
            if beg < end <= 255:
                for i in range(beg, end + 1):
                    individuals.add(f"{prefix}.{i}")
            else:
                # TODO: invalid range
                pass
        else:
            individuals.add(base_ip)

    # Combining individual and CIDR addresses only necessary if we do not split the CIDRS
    if not split_cidr:
        # Keep only individual IPs that are not covered by a CIDR
        for ip in individuals:
            ip_obj = ipaddress.ip_address(ip)
            if not any(ip_obj in net for net in cidrs):
                unique_entries.append(ip)

        # Append each CIDR entry
        for cidr in cidrs:
            unique_entries.append(str(cidr))

    # Sort the list numerically
    return sorted(unique_entries, key=lambda x: ipaddress.ip_address(x.split('/')[0]))