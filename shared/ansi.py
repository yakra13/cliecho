
import os
import re
import sys
from enum import Enum, auto

# Regex to remove ANSI escape characters from a string
ANSI_REGEX = re.compile(r'\x1b\[[0-9;]*m')

class AnsiSupport(Enum):
    """Enum with ANSI color support levels."""
    NONE      = auto()
    ANSI_16   = auto()
    ANSI_256  = auto()
    TRUECOLOR = auto()


class AnsiStyle(Enum):
    """Enum containing ANSI styling options: bold, underline, etc."""
    BOLD      = '1'
    DIM       = '2'
    ITALIC    = '3'
    UNDERLINE = '4'
    BLINK     = '5'
    REVERSE   = '6'
    HIDDEN    = '7'
    STRIKE    = '8'


def _detect_ansi_support() -> AnsiSupport:
    """
    Attempts to determine what ANSI format is supported by the terminal.

    Args:
        None

    Returns:
        Level of ANSI encoding supported by the current terminal:
        None, ANSI 16, ANSI 256, Truecolor
    
    Raises:
        None
    """
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
    """
    Removes any ANSI encoding in a given string.
    
    Args:
        text: The text to strip ANSI encoding from.
    
    Returns:
        Original text with all ANSI encoding removed.
    
    Raises:
        None
    """
    return ANSI_REGEX.sub('', text)

def visible_len(text: str) -> int:
    """
    Gets the length of text ignoring any ANSI encoding.

    Args:
        text: The text to get the length of.
    
    Returns:
        Integer of the text ignoring ANSI encoding characters.
    
    Raises:
        None
    """
    return len(strip_ansi(text))

def center_ansi(text: str, width: int, fill_char: str = ' ') -> str:
    """
    Performs a center operation on the given text; ignoring any ANSI encoding.
    
    Args:
        text: The text to center.
        width: Width of the resulting string for the text to be centered in.
        fill_char: The character to pad the text with.
    
    Returns:
        The original text with ANSI encoding intact and properly centered.
    
    Raises:
        None
    """
    text_width = visible_len(text)
    padding = max(0, width - text_width)
    pad_text = fill_char * (padding // 2)

    # No padding required
    if padding == 0:
        return text

    # Use default fill char if empty string provided
    if fill_char == '':
        fill_char = ' '

    # Use only the first character if multiple provided
    fill_char = fill_char[0]

    # Evenly place padding on either side of the text
    # On odd padding the left side gets the additional padding character
    return f"{pad_text}{fill_char if padding % 2 == 0 else ''}{text}{pad_text}"

def ljust_ansi(text: str, width: int, fill_char: str = ' ') -> str:
    """
    Performs a left justify operation on the given text; ignoring any ANSI encoding.
    
    Args:
        text: The text to left justify.
        width: Width of the resulting string for the text to be left justified.
        fill_char: The character to pad the text with.
    
    Returns:
        The original text with ANSI encoding intact and properly left justified.
    
    Raises:
        None
    """
    text_width = visible_len(text)
    padding = max(0, width - text_width)

    # No padding required
    if padding == 0:
        return text

    # Use default fill char if empty string provided
    if fill_char == '':
        fill_char = ' '

    # Use only the first character if multiple provided
    fill_char = fill_char[0]
    
    return f"{text}{fill_char * padding}"

def rjust_ansi(text: str, width: int, fill_char: str = ' ') -> str:
    """
    Performs a right justify operation on the given text; ignoring any ANSI encoding.
    
    Args:
        text: The text to right justify.
        width: Width of the resulting string for the text to be right justified.
        fill_char: The character to pad the text with.
    
    Returns:
        The original text with ANSI encoding intact and properly right justified.
    
    Raises:
        None
    """
    text_width = visible_len(text)
    padding = max(0, width - text_width)

    # No padding required
    if padding == 0:
        return text

    # Use default fill char if empty string provided
    if fill_char == '':
        fill_char = ' '

    # Use only the first character if multiple provided
    fill_char = fill_char[0]
    
    return f"{fill_char * padding}{text}"

# Determine supported ANSI at instantiation
SUPPORTED_ANSI = _detect_ansi_support()