from functools import cache
import ipaddress
import os
from typing import Final

MAX_INT8:  Final[int] = 2**(8 - 1) - 1
MAX_INT16: Final[int] = 2**(16 - 1) - 1
MAX_INT32: Final[int] = 2**(32 - 1) - 1
MAX_INT64: Final[int] = 2**(64 - 1) - 1

MAX_UINT8:  Final[int] = 2**8 - 1
MAX_UINT16: Final[int] = 2**16 - 1
MAX_UINT32: Final[int] = 2**32 - 1
MAX_UINT64: Final[int] = 2**64 - 1

MIN_INT8:  Final[int] = -2**(8 - 1)
MIN_INT16: Final[int] = -2**(16 - 1)
MIN_INT32: Final[int] = -2**(32 - 1)
MIN_INT64: Final[int] = -2**(64 - 1)

MIN_UINT8:  Final[int] = 0
MIN_UINT16: Final[int] = 0
MIN_UINT32: Final[int] = 0
MIN_UINT64: Final[int] = 0

def clamp_int8(value: int) -> int:
    return max(MIN_INT8, min(MAX_INT8, int(value)))

def clamp_int16(value: int) -> int:
    return max(MIN_INT16, min(MAX_INT16, int(value)))

def clamp_int32(value: int) -> int:
    return max(MIN_INT32, min(MAX_INT32, int(value)))

def clamp_int64(value: int) -> int:
    return max(MIN_INT64, min(MAX_INT64, int(value)))

def clamp_uint8(value: int) -> int:
    return max(MIN_UINT8, min(MAX_UINT8, int(value)))

def clamp_uint16(value: int) -> int:
    return max(MIN_UINT16, min(MAX_UINT16, int(value)))

def clamp_uint32(value: int) -> int:
    return max(MIN_UINT32, min(MAX_UINT32, int(value)))

def clamp_uint64(value: int) -> int:
    return max(MIN_UINT64, min(MAX_UINT64, int(value)))

def lerp(a: float, b: float, t: float) -> float:
    t = max(0.0, min(1.0, t))
    return a + (b - a) * t

@cache
def get_system_max_threads() -> int:
    """Calculates system thread capacity once and stores the result."""
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:
        return os.cpu_count() or 1

import re

IP_PATTERN = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){3})(?:\/(\d{1,2})|\-(\d{1,3}))?$')

def parse_ips(addresses: str, split_cidr: bool = False) -> List[str]:
    # 192.168.0.2-10, 192.168.1.0/24, 192.168.2.2
    # split on commas
    unique_entries = set()

    raw = [p.strip() for p in addresses.split(',')]

    for part in raw:
        match = IP_PATTERN.match(part)
        if not match:
            # TODO: invalid formatting
            continue

        base_ip, cidr_bits, range_end = match.groups()

        if cidr_bits:
            try:
                net = ipaddress.ip_network(f"{base_ip}/{cidr_bits}", strict=False)
                #TODO:
                if split_cidr:
                    pass
                else:
                    unique_entries.add(str(net))
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
                    unique_entries.add(f"{prefix}.{i}")
            else:
                # TODO: invalid range
                pass
        else:
            unique_entries.add(base_ip)

    # Sort the list numerically
    return sorted(list(unique_entries), key=lambda x: ipaddress.ip_address(x.split('/')[0]))