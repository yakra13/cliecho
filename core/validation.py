from ipaddress import ip_address, ip_network
from typing import Any, Iterable, Tuple

from core.exceptions import GuardrailError

class Port():
    MIN = 0
    MAX = 65535
    MASK = 0xFFFF

def _parse_ip(entry: str):
    # CIDR
    if '/' in entry:
        return ip_network(entry, strict=False)

    # Shorthand
    if '-' in entry:
        base, hosts = entry.rsplit('.', 1)
        beg, end = hosts.split('-', 1)

        if not 0 <= int(beg) <= int(end) <= 255:
            raise ValueError(f"Invalid IP range: {entry}")

        start_ip = ip_address(f"{base}.{beg}")
        end_ip   = ip_address(f"{base}.{end}")

        return (start_ip, end_ip)

    return ip_network(entry + "/32", strict=False)

def validate_ip(address: str, guard_rails: Iterable[str]) -> bool:
    """
    """
    # 192.168.0.1-150, 192.168.0.175, 172.9.0.0/12
    # Check if it is a valid ip address
    ip_addr = ip_address(address)

    for entry in guard_rails:
        parsed = _parse_ip(entry)

        # If parsed is a shorthand range
        if isinstance(parsed, tuple):
            start, end = parsed
            if start <= ip_addr <= end:
                return True
        else:
            if ip_addr in parsed:
                return True

    return False

def _parse_port(entry: str) -> int | Tuple[int, int]:
    if '-' in entry:
        beg, end = entry.split('-', 1)

        try:
            beg = int(beg)
            end = int(end)
        except ValueError as e:
            raise ValueError from e

        return (beg, end)

    try:
        entry = int(entry)
    except ValueError as e:
        raise ValueError from e

    return entry

def validate_port(port: str | int, guard_rails: Iterable[str]) -> bool:
    try:
        port = int(port)
    except ValueError as e:
        raise ValueError from e

    if not 0 <= port <= 65535:
        return False

    for entry in guard_rails:
        try:
            parsed = _parse_port(entry)
        except ValueError as e:
            raise GuardrailError(entry) from e

        if isinstance(parsed, tuple):
            start, end = parsed
            if start <= port <= end:
                return True
        elif port == parsed:
            return True

    return False
