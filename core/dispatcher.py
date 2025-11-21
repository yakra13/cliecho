from typing import Optional, Type
from module_base import ModuleBase
from core.module_loader import ModuleLoader
from output_formatter import format_module_settings
from core.exceptions import NoModuleSelectedError

class Dispatcher:
    _loaded_modules: dict[str, ModuleBase] = {}
    _current_module: Optional[ModuleBase] = None

    def __init__(self, module_loader: ModuleLoader):
        self._module_loader: ModuleLoader = module_loader
        # self.module_class = module_class
        # self.instance = module_class()
    
    def set_current_module(self, module_name: str) -> None:
        # USE MODULE
        if not self._loaded_modules.get(module_name):
            # module not loaded
            module: Type[ModuleBase] = self._module_loader.load(module_name)
            try:
                self._loaded_modules[module_name] = module()
            except RuntimeError as e:
                # TODO: log and inform user selected module could not be loaded
                # Pass up config.yml not found
                pass
        
        if self._current_module is not None:
            # TODO: unload module if necessary
            self._current_module = self._loaded_modules[module_name]

    def print_current_module_settings(self) -> str:
        # Get current module args and current arg settings
        if self._current_module is None:
            raise NoModuleSelectedError()
        
        return format_module_settings(self._current_module.get_current_settings())
        