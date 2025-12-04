from typing import Dict, Tuple, Any

from shared.module_base import ModuleArg

def format_module_settings(module_settings: Dict[str, Tuple[ModuleArg, Any | None]]) -> str:
    raise NotImplementedError("format_module_settings: Not implemented")

def format_show_modules(modules: Dict[str, Dict[str, str]]) -> str:
    raise NotImplementedError("format_show_modules: Not implemented")