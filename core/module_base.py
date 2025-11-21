from importlib import resources
import yaml

from typing import Optional, Union, List, Dict, Tuple, Any, final
from dataclasses import dataclass

@dataclass
class ModuleArg:
    description: str
    required: bool = False    
    default_value: Optional[Union[str, List[str]]] = None
    help: Optional[str] = None
    shortname: Optional[str] = None

class ModuleBase:
    _metadata = None
    _module_args: Dict[str, ModuleArg] = {}
    _description: str = ''
    _options: Dict[str, Any] = {}

    def __init__(self):
        pkg = self.__class__.__module__   # "modules.modulename"

        try:
            cfg_path = resources.files(pkg) / "config.yml"
        except Exception as e:
            raise RuntimeError(f"Cannot locate config.yml for module '{pkg}'") from e

        with cfg_path.open("r", encoding="utf-8") as f:
            self.metadata = yaml.safe_load(f)

        self.description = self.metadata["description"]

        args = self.metadata["arguments"]

        # Parse required args
        for name, spec in args.get("required", {}).items():
            self._module_args[name] = ModuleArg(
                description   = spec["description"],
                required      = True,
                default_value = spec.get("default"),
                help          = spec.get("help"),
                shortname     = spec.get("shortname"),
            )
            # Assign any args with default values
            if self._module_args[name].default_value:
                self._options[name] = self._module_args[name].default_value

        # Parse optional args
        for name, spec in args.get("optional", {}).items():
            self._module_args[name] = ModuleArg(
                description   = spec["description"],
                required      = False,
                default_value = spec.get("default"),
                help          = spec.get("help"),
                shortname     = spec.get("shortname"),
            )
            # Assign any args with default values
            if self._module_args[name].default_value:
                self._options[name] = self._module_args[name].default_value

    @final
    def set_param(self, key, val):
        if key not in self._module_args:
            raise ValueError(f"Unknown option {key}")
        
        self._options[key] = val

    @final    
    def get_param(self, key):
        if key not in self._module_args:
            raise KeyError(f"Unknown option '{key}'")
        
        return self._options.get(key)
    
    @final
    def get_current_settings(self) -> Dict[str, Tuple[ModuleArg, Any]]:
        settings: Dict[str, Tuple[ModuleArg, Any]] = {}
        for name, arg in self._module_args.items():
            current_value: Any = self._options.get(name)
            settings[name] = (arg, current_value)

        return settings

    @final    
    def validate(self):
        missing_args: List[str] = []
        
        for name, arg in self._module_args.items():
            if arg.required and self._options.get(name) is None:
                missing_args.append(name)
        
        if missing_args:
            raise ValueError(f"Missing required options: {', '.join(missing_args)}")


    def run(self):
        # TODO: perform run logging
        raise NotImplementedError("Module must implement run()")