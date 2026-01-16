
# Regex to remove ANSI escape characters from a string
import os
import re
import sys
from enum import Enum, auto

ANSI_REGEX = re.compile(r'\x1b\[[0-9;]*m')

class AnsiSupport(Enum):
    NONE      = auto()
    ANSI_16   = auto()
    ANSI_256  = auto()
    TRUECOLOR = auto()

class AnsiStyle(Enum):
    BOLD      = '1'
    DIM       = '2'
    ITALIC    = '3'
    UNDERLINE = '4'
    BLINK     = '5'
    REVERSE   = '6'
    HIDDEN    = '7'
    STRIKE    = '8'


def _detect_ansi_support() -> AnsiSupport:
    """Attempts to determine what ANSI format is supported by the terminal."""
    # stdout must be a TTY
    if not sys.stdout.isatty():
        return AnsiSupport.NONE

    # check explicit user override
    if os.environ.get("NO_COLOR"):
        return AnsiSupport.NONE

    if os.environ.get("FORCE_COLOR"):
        return AnsiSupport.TRUECOLOR
    
    term = os.environ.get("TERM", "").lower()
    colorterm = os.environ.get("COLORTERM", "").lower()

    # truecolor detection
    if colorterm in ("truecolor", "24bit"):
        return AnsiSupport.TRUECOLOR

    if "truecolor" in term or "24bit" in term:
        return AnsiSupport.TRUECOLOR

    if "256color" in term:
        return AnsiSupport.ANSI_256

    # Windows
    if sys.platform == "win32":
        # Terminal, VS code, conhost
        if os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM"):
            return AnsiSupport.TRUECOLOR
        return AnsiSupport.ANSI_16

    return AnsiSupport.ANSI_16

def strip_ansi(text: str) -> str:
    return ANSI_REGEX.sub('', text)

def visible_len(text: str) -> int:
    return len(strip_ansi(text))

def center_ansi(text: str, width: int, fillchar: str = ' ') -> str:
    text_width = visible_len(text)
    padding = max(0, width - text_width)

    # Use default fill char if empty string provided
    if fillchar == '':
        fillchar = ' '

    # Use only the first character if multiple provided
    fillchar = fillchar[0]
    
    if padding == 0:
        # no padding required
        return text
    elif padding % 2 == 0:
        # evenly place padding on either side of the text
        text = f"{fillchar * (padding // 2)}{text}{fillchar * (padding // 2)}"
    else:
        # extra padding on odd padding values is placed on the left
        text = f"{fillchar * ((padding // 2) + 1)}{text}{fillchar * (padding // 2)}"

    return text

def ljust_ansi(text: str, width: int, fillchar: str = ' ') -> str:
    text_width = visible_len(text)
    padding = max(0, width - text_width)

    # Use default fill char if empty string provided
    if fillchar == '':
        fillchar = ' '

    # Use only the first character if multiple provided
    fillchar = fillchar[0]

    if padding == 0:
        # no padding required
        return text
    
    return f"{text}{fillchar * padding}"

def rjust_ansi(text: str, width: int, fillchar: str = ' ') -> str:
    text_width = visible_len(text)
    padding = max(0, width - text_width)

    # Use default fill char if empty string provided
    if fillchar == '':
        fillchar = ' '

    # Use only the first character if multiple provided
    fillchar = fillchar[0]

    if padding == 0:
        # no padding required
        return text
    
    return f"{fillchar * padding}{text}"

SUPPORTED_ANSI = _detect_ansi_support()