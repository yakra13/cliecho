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

