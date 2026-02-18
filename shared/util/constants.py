# --- Signed Integers (int) ---
# 8-bit
from typing import Final


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