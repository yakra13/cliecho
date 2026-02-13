"""

"""
from datetime import datetime
import math
import shutil

from typing import Any, Dict, Iterable, List, Optional, Tuple

# from shared.module_base import ModuleArg

from shared.ansi import AnsiStyle, AnsiSupport, ljust_ansi, visible_len, SUPPORTED_ANSI
from shared.color import Color, estimate_ansi_color
from shared.module_logger import EventLog


class Formatter:
    def format(self, event: EventLog) -> str:
        return ''

class JsonFormatter(Formatter):
    def format(self, event: EventLog) -> str:
        import json
        return json.dumps(event.to_dict(), separators=(',', ':'))


def _to_column_major(items: List[str], columns: int) -> List[str]:
    """
    Converts a sorted list to unix column major order.

    Args:
        items: List of strings to sort.
        columns: The number of columns to fit the items into.

    Returns:
        A sorted list that when printed to termina will be column major order.

    Raises:
        None
    """
    if not items or columns <= 0:
        return items
    
    rows = math.ceil(len(items) / columns)

    # Create a 2D list large enough to fit all items
    grid: List[List[Optional[str]]] = [[None] * columns for _ in range(rows)]

    # Populate the list with each item top to bottom; left to right
    idx = 0
    for col in range(columns):
        for row in range(rows):
            if idx < len(items):
                grid[row][col] = items[idx]
                idx += 1

    result: List[str] = []
    # Transform the 2D list to 1D
    for row in grid:
        for item in row:
            result.append(item if item is not None else '')
    
    return result

def format_list_as_grid(items: List[str],
                        columns: int = 1,
                        auto_size: bool = False,
                        column_major: bool = True,
                        left_padding: int = 4) -> str:
    """
    Formats a list of strings into a grid. Maintains any ANSI encoding.
    
    Args:
        items: List of strings to be formatted into a grid
        columns: The explicit number of columns the grid should contain if possible.
        auto_size: If true the grid will be sized automatically and ignore the columns arg
        column_major: Determines if the grid will fill top to bottom then left to right
        left_padding: the number of padding spaces to insert before each row

    Returns:
        Returns a string formatted to be printed in a grid.
        If there are no items an empty string is returned.

    Raises:
        None
    """
    if not items:
        return ''
    
    padding: str = ' ' * left_padding

    # Find the length of the longest item add 2 for spacing
    column_width = max(visible_len(item) for item in items) + 2

    if auto_size:
        terminal_width, _ = shutil.get_terminal_size()
        columns = max(1, terminal_width // column_width)

    if column_major and len(items) > columns:
        items = _to_column_major(items, columns)

    # Print formatted
    lines = []

    for i in range(0, len(items), columns):
        row_items = items[i:i + columns]
        line = ''.join(ljust_ansi(item, column_width) for item in row_items)
        lines.append(f"{padding}{line.rstrip()}")  # remove trailing spaces


    return '\n'.join(lines)

# def format_module_settings(module_settings: Dict[str, Tuple[ModuleArg, Optional[Any]]]) -> str:
#     """
#     Docstring for format_module_settings
    
#     :param module_settings: Description
#     :type module_settings: Dict[str, Tuple[ModuleArg, Optional[Any]]]
#     :return: Description
#     :rtype: str
#     """
#     raise NotImplementedError("format_module_settings: Not implemented")

def format_timestamp_console(timestamp: datetime) -> str:
    """
    Returns a formatted string of the timestamp.
    example: 2000-01-01 23:00:00

    Args:
        timestamp: The timestamp to format.

    Returns:
        A formatted string representing the timestamp.

    Raises:
        None
    """
    # TODO: make nicer (fix for circular import)
    from ..core.config import CONFIG
    return timestamp.strftime(CONFIG.timestamp_format)

def format_timestamp_epoch(timestamp: datetime) -> str:
    """
    Returns a string of the timestamp in epoch format.
    ie number of seconds since Jan 1, 1970 UTC

    Args:
        timestamp: The timestamp to format.

    Returns:
        A string representing the timestamp in epoch format.

    Raises:
        None
    """
    return str(int(timestamp.timestamp()))

def style_text(text: str,
               text_color: Optional[Color] = None,
               back_color: Optional[Color] = None,
               styles: Optional[Iterable[AnsiStyle]] = None) -> str:
    """
    Apply ANSI color and text styling to a string.

    If the current terminal does not support the requested formatting,
    the original text is returned unmodified.

    Args:
        text: The text to be styled.
        text_color: Optional foreground color.
        back_color: Optional background color.
        styles: Optional iterable of text styles (e.g. bold, underline).

    Returns:
        The stylized text if supported; otherwise, the original text.

    Raises:
        None

    """
    from core.config import CONFIG
    if SUPPORTED_ANSI == AnsiSupport.NONE or not CONFIG.enable_ansi:
        # NOTE: We assume that even styling is not supported (bold, underline, etc)
        return text

    codes = []

    if styles:
        codes.extend([s.value for s in styles])

    if text_color:
        if SUPPORTED_ANSI == AnsiSupport.TRUECOLOR:
            codes.extend(['38', '2', str(text_color.R), str(text_color.G), str(text_color.B)])
        else:
            # If truecolor is not supported we default to ANSI_16 currently
            fg = estimate_ansi_color(text_color)
            codes.extend([str(fg)])
    
    if back_color:
        if SUPPORTED_ANSI == AnsiSupport.TRUECOLOR:
            codes.extend(['48', '2', str(back_color.R), str(back_color.G), str(back_color.B)])
        else:
            # If truecolor is not supported we default to ANSI_16 currently
            bg = estimate_ansi_color(back_color, is_background=True)
            # Add ten to shift from foreground ansi color to background
            bg += 10
            codes.extend([str(bg)])

    seq = ';'.join(codes)

    return f"\033[{seq}m{text}\033[0m"