"""
"""
import shutil
from typing import Dict, Tuple, Any, Optional, List

from shared.module_base import ModuleArg

def format_module_settings(module_settings: Dict[str, Tuple[ModuleArg, Optional[Any]]]) -> str:
    """
    Docstring for format_module_settings
    
    :param module_settings: Description
    :type module_settings: Dict[str, Tuple[ModuleArg, Optional[Any]]]
    :return: Description
    :rtype: str
    """
    raise NotImplementedError("format_module_settings: Not implemented")

def format_show_modules(modules: List[str]) -> str:
    """
    Docstring for format_show_modules
    
    :param modules: Description
    :type modules: List[str]
    :return: Description
    :rtype: str
    """
    if not modules:
        return ""

    cols, _ = shutil.get_terminal_size()

    max_len = max(len(m) for m in modules) + 2

    items_per_row = max(1, cols // max_len)

    # Print formatted
    lines = []
    for i in range(0, len(modules), items_per_row):
        row_items = modules[i:i + items_per_row]
        line = "".join(item.ljust(max_len) for item in row_items)
        lines.append(line.rstrip())  # remove trailing spaces

    return "\n".join(lines)
    # raise NotImplementedError("format_show_modules: Not implemented")
