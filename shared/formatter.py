import math
import os
import re
import shutil
import sys

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, ClassVar, Final, Iterable, List, Literal, Optional

from .ansi import AnsiStyle, AnsiSupport, visible_len, SUPPORTED_ANSI
from .color import Color, estimate_ansi_color

def _to_column_major(items: List[str], columns: int) -> List[str]:
    """Converts a sorted list to unix column major order."""
    if not items or columns <= 0:
        return items
    
    rows = math.ceil(len(items) / columns)

    grid: List[List[Optional[str]]] = [[None] * columns for _ in range(rows)]

    # Fill column-major
    idx = 0
    for c in range(columns):
        for r in range(rows):
            if idx < len(items):
                grid[r][c] = items[idx]
                idx += 1

    result: List[str] = []
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

    # Find the length of the longest item add 2 for spacing
    column_width = max(visible_len(item) for item in items) + 2

    if auto_size:
        terminal_width, _ = shutil.get_terminal_size()
        columns = max(1, terminal_width // column_width)

    if column_major:
        items = _to_column_major(items, columns)

    # Print formatted
    lines = []

    for i in range(0, len(items), columns):
        row_items = items[i:i + columns]
        line = ''.join(item.ljust(column_width) for item in row_items)
        lines.append(f"{' ' * left_padding}{line.rstrip()}")  # remove trailing spaces

    return '\n'.join(lines)

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
    if SUPPORTED_ANSI == AnsiSupport.NONE:
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
            bg = estimate_ansi_color(back_color)
            # Add ten to shift from foreground ansi color to background
            bg += 10
            codes.extend([str(bg)])

    seq = ';'.join(codes)

    return f"\033[{seq}m{text}\033[0m"