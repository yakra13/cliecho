import yaml
from dataclasses import dataclass
from importlib import resources
from queue import Queue
from typing import Optional, Union, List, Dict, Tuple, Type, Any, final

@dataclass
class ModuleArg:
    description: str
    required: bool = False    
    default_value: Optional[Union[str, List[str]]] = None
    help: Optional[str] = None
    shortname: Optional[str] = None
    value_type: Type = str

class ModuleBase:
    def __init__(self):
        self._metadata = None
        self._module_args: Dict[str, ModuleArg] = {}
        self._name: str = ''
        self._description: str = ''
        self._options: Dict[str, Any] = {}
        # If no Queue is provided by the core then logging is handled internally
        self._message_queue: Optional[Queue] = None

        pkg = self.__class__.__module__   # "modules.modulename"

        try:
            cfg_path = resources.files(pkg) / "config.yml"
        except Exception as e:
            raise RuntimeError(f"Cannot locate config.yml for module '{pkg}'") from e

        with cfg_path.open("r", encoding="utf-8") as f:
            self._metadata = yaml.safe_load(f)

        self._name = self._metadata["name"]
        self._description = self._metadata["description"]

        args = self._metadata["arguments"]

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

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description

    @property
    def options(self) -> Dict[str, ModuleArg]:
        return self._module_args

    @property
    def message_queue(self) -> Optional[Queue]:
        return self._message_queue
    
    @message_queue.setter
    def message_queue(self, queue: Queue) -> None:
        self._message_queue = queue

    @final
    def set_param(self, key: str, val: str):
        if key not in self._module_args:
            raise KeyError(f"Unknown option {key}")
        
        try:
            self._options[key] = self._module_args[key].value_type(val)
        except:
            raise ValueError()

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

    def _log(self, message: str):
        if self._message_queue:
            self._message_queue.put(message)
            return
        
        # TODO: there is no core present to pass messages to so we will handle logging

    def run(self):
        # TODO: perform run logging
        raise NotImplementedError("Module must implement run()")