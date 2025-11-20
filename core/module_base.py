from importlib import resources
import yaml

from typing import Optional, Union, List, Dict
from dataclasses import dataclass

@dataclass
class ModuleArg:
    description: str
    required: bool = False    
    default_value: Optional[Union[str, List[str]]] = None
    help: Optional[str] = None
    shortname: Optional[str] = None

class ModuleBase:
    metadata = None
    module_args: Dict[str, ModuleArg] = {}
    description: str = ''
    options = {}

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
            self.module_args[name] = ModuleArg(
                description   = spec["description"],
                required      = True,
                default_value = spec.get("default"),
                help          = spec.get("help"),
                shortname     = spec.get("shortname"),
            )
            # Assign any args with default values
            if self.module_args[name].default_value:
                self.options[name] = self.module_args[name].default_value

        # Parse optional args
        for name, spec in args.get("optional", {}).items():
            self.module_args[name] = ModuleArg(
                description   = spec["description"],
                required      = False,
                default_value = spec.get("default"),
                help          = spec.get("help"),
                shortname     = spec.get("shortname"),
            )
            # Assign any args with default values
            if self.module_args[name].default_value:
                self.options[name] = self.module_args[name].default_value

    def set_param(self, key, val):
        if key not in self.module_args:
            raise ValueError(f"Unknown option {key}")
        
        self.options[key] = val
    
    def get_param(self, key):
        if key not in self.module_args:
            raise KeyError(f"Unknown option '{key}'")
        
        return self.options.get(key)
    
    def validate(self):
        missing_args: List[str] = []
        
        for name, arg in self.module_args.items():
            if arg.required and self.options.get(name) is None:
                missing_args.append(name)
        
        if missing_args:
            raise ValueError(f"Missing required options: {', '.join(missing_args)}")


    def run(self):
        raise NotImplementedError("Module must implement run()")