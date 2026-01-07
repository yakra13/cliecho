"""
"""
import math
import shutil
from typing import Dict, Tuple, Any, Optional, List

from shared.module_base import ModuleArg

def to_column_major(items: List[str], columns: int) -> List[str]:
    if not items or columns <= 0:
        return items
    
    rows = math.ceil(len(items) / columns)
    result: List[str] = []
    for r in range(rows):
        for c in range(columns):
            idx = c * rows + r
            if idx < len(items):
                result.append(items[idx])
    
    return result

def format_module_settings(module_settings: Dict[str, Tuple[ModuleArg, Optional[Any]]]) -> str:
    """
    Docstring for format_module_settings
    
    :param module_settings: Description
    :type module_settings: Dict[str, Tuple[ModuleArg, Optional[Any]]]
    :return: Description
    :rtype: str
    """
    raise NotImplementedError("format_module_settings: Not implemented")

def format_list_as_table(items: List[str], columns: int = 1, auto_size: bool = False, column_major: bool = True) -> str:
    """
    Docstring for format_show_modules
    """

    if not items:
        return ''

    # Find the length of the longest item
    # TODO: need to strip ANSI color codes for m
    column_width = max(len(item) for item in items) + 2

    if auto_size:
        terminal_width, _ = shutil.get_terminal_size()
        columns = max(1, terminal_width // column_width)

    if column_major:
        items = to_column_major(items, columns)

    # Print formatted
    lines = []
    # TODO: support both (only first currently):
    # a b c
    # d e f
    # and
    # a c e
    # b d f
    for i in range(0, len(items), columns):
        # TODO: the column problem is here
        row_items = items[i:i + columns]
        line = ''.join(item.ljust(column_width) for item in row_items)
        lines.append(f"    {line.rstrip()}")  # remove trailing spaces

    return '\n'.join(lines)
