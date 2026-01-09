"""
"""
import math
import shutil
import re

from typing import Dict, Tuple, Any, Optional, List

from shared.module_base import ModuleArg

# Regex to remove ANSI escape characters from a string
ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

def to_column_major(items: List[str], columns: int) -> List[str]:
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


    # for r in range(rows):
    #     for c in range(columns):
    #         idx = c * rows + r
    #         if idx < len(items):
    #             result.append(items[idx])
    
    return result

def visible_length(s: str) -> int:
    # Remove ANSI escape characters for proper string length
    return len(ANSI_RE.sub('', s))

def format_module_settings(module_settings: Dict[str, Tuple[ModuleArg, Optional[Any]]]) -> str:
    """
    Docstring for format_module_settings
    
    :param module_settings: Description
    :type module_settings: Dict[str, Tuple[ModuleArg, Optional[Any]]]
    :return: Description
    :rtype: str
    """
    raise NotImplementedError("format_module_settings: Not implemented")

def format_list_as_table(items: List[str],
                         columns: int = 1,
                         auto_size: bool = False,
                         column_major: bool = True) -> str:
    """
    Docstring for format_show_modules
    """

    if not items:
        return ''

    # Find the length of the longest item and 2 for spacing
    column_width = max(visible_length(item) for item in items) + 2

    if auto_size:
        terminal_width, _ = shutil.get_terminal_size()
        columns = max(1, terminal_width // column_width)

    if column_major:
        items = to_column_major(items, columns)

    # Print formatted
    lines = []

    for i in range(0, len(items), columns):
        row_items = items[i:i + columns]
        line = ''.join(item.ljust(column_width) for item in row_items)
        lines.append(f"    {line.rstrip()}")  # remove trailing spaces

    return '\n'.join(lines)
