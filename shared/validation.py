from datetime import datetime
# from functools import cache
from ipaddress import ip_address, ip_network
import os
from pathlib import Path
from typing import Any, Callable, Iterable, NamedTuple, Optional, Tuple, Union

# from core.exceptions import GuardrailError
from shared.util import MAX_UINT16, MIN_UINT16

class Port():
    MIN = 0
    MAX = 65535
    MASK = 0xFFFF

# class IPAddress():


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

# def validate_ip(address: str, guard_rails: Iterable[str]) -> bool:
#     """
#     """
#     # 192.168.0.1-150, 192.168.0.175, 172.9.0.0/12
#     # Check if it is a valid ip address
#     ip_addr = ip_address(address)

#     for entry in guard_rails:
#         parsed = _parse_ip(entry)

#         # If parsed is a shorthand range
#         if isinstance(parsed, tuple):
#             start, end = parsed
#             if start <= ip_addr <= end:
#                 return True
#         else:
#             if ip_addr in parsed:
#                 return True

#     return False

# def _parse_port(entry: str) -> int | Tuple[int, int]:
#     if '-' in entry:
#         beg, end = entry.split('-', 1)

#         try:
#             beg = int(beg)
#             end = int(end)
#         except ValueError as e:
#             raise ValueError from e

#         return (beg, end)

#     try:
#         entry = int(entry)
#     except ValueError as e:
#         raise ValueError from e

#     return entry

# def validate_port(port: str | int, guard_rails: Iterable[str]) -> bool:
#     try:
#         port = int(port)
#     except ValueError as e:
#         raise ValueError from e

#     if not 0 <= port <= 65535:
#         return False

#     for entry in guard_rails:
#         try:
#             parsed = _parse_port(entry)
#         except ValueError as e:
#             raise GuardrailError(entry) from e

#         if isinstance(parsed, tuple):
#             start, end = parsed
#             if start <= port <= end:
#                 return True
#         elif port == parsed:
#             return True

#     return False


class ValidationResult(NamedTuple):
    is_valid: bool
    error: Optional[str] = None

Validator = Callable[[Any], ValidationResult]

# TODO: place this in util or something
# @cache
# def get_system_max_threads() -> int:
#     """Calculates system thread capacity once and stores the result."""
#     try:
#         return len(os.sched_getaffinity(0))
#     except AttributeError:
#         return os.cpu_count() or 1

# _last_error: Optional[str] = None

# def get_last_error() -> Optional[str]:
#     return _last_error

def is_directory(path: Union[Path, str]) -> bool:
    p = Path(path)
    return not p.is_file()

def is_in_range(min_val: Union[int, float], max_val: Union[int, float]) -> Validator:
    def validate(value: Any) -> ValidationResult:
        # global _last_error
        # _last_error = None

        if not isinstance(value, (int, float)):
            # _last_error = f"Input '{value}' is a {type(value).__name__}, expected a number"
            return ValidationResult(False, f"'{value}' is not a number")

        if min_val <= value <= max_val:
            return ValidationResult(True)

        return ValidationResult(False)

    return validate

def is_port(port: int) -> ValidationResult:
    # 1-65535
    func = is_in_range(MIN_UINT16 + 1, MAX_UINT16)
    return func(port)

def is_timestamp(format_str: str) -> ValidationResult:
    try:
        datetime.now().strftime(format_str)
    except (ValueError, TypeError):
        return ValidationResult(False)

    return ValidationResult(True)

def is_ip_address(address: Union[str, int]) -> ValidationResult:
    try:
        addr = ip_address(address)
    except ValueError:
        return ValidationResult(False)
    
    return ValidationResult(True)

# def is_ip_list_format(input_str: str) -> ValidationResult:


# def thread_count(max_threads: int) -> bool:
#     """
#     Get the maximum thread count and check value falls within the range of
#     0 to maximum thread count.
#     """
#     # max_count: int = 0
#     # try:
#     #     max_count = len(os.sched_getaffinity(0))
#     # except AttributeError:
#     #     max_count = os.cpu_count() or 1
    
#     return 0 <= int(max_threads) <= get_system_max_threads()
