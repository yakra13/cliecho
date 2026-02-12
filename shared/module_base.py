"""
Docstring for shared.module_base
"""
import yaml
from dataclasses import dataclass
from importlib import resources
from typing import Optional, Union, Type, Any, List, Dict, final

from shared.module_logger import LOGGER

@dataclass
class ModuleArg:
    """Dataclass representing a module argument and its settings."""
    description: str
    is_required: bool = False    
    default_value: Optional[Union[str, List[str]]] = None
    help: Optional[str] = None
    shortname: Optional[str] = None
    category: Type = str


class ModuleBase:
    """
    Docstring for ModuleBase
    """
    def __init__(self, threaded: bool = False):
        self._metadata = None
        self._module_args: Dict[str, ModuleArg] = {}
        self._name: str = ''
        self._description: str = ''
        self._options: Dict[str, Any] = {}
        # If no Queue is provided by the core then logging is handled internally
        # self._message_queue: Optional[Queue[Event]] = None

        pkg = self.__class__.__module__   # "modules.modulename"

        try:
            cfg_path = resources.files(pkg) / "config.yml"
        except Exception as e:
            raise RuntimeError(f"Cannot locate config.yml for module '{pkg}'") from e

        with cfg_path.open("r", encoding="utf-8") as f:
            self._metadata = yaml.safe_load(f)

        self._name        = pkg #self._metadata["name"]
        self._description = self._metadata["description"]
        args              = self._metadata["arguments"]

        # Parse required args
        for name, spec in args.get("required", {}).items():
            self._module_args[name] = ModuleArg(
                description   = spec["description"],
                is_required      = True,
                default_value = spec.get("default"),
                help          = spec.get("help"),
                shortname     = spec.get("shortname"),
                category      = spec.get("category")
            )
            # Assign any args with default values
            if self._module_args[name].default_value:
                self._options[name] = self._module_args[name].default_value

        # Parse optional args
        for name, spec in args.get("optional", {}).items():
            self._module_args[name] = ModuleArg(
                description   = spec["description"],
                is_required      = False,
                default_value = spec.get("default"),
                help          = spec.get("help"),
                shortname     = spec.get("shortname"),
            )
            # Assign any args with default values
            if self._module_args[name].default_value:
                self._options[name] = self._module_args[name].default_value

    @property
    def name(self) -> str:
        """
        Docstring for name
        
        :param self: Description
        :return: Description
        :rtype: str
        """
        return self._name

    @property
    def description(self) -> str:
        """
        Docstring for description
        
        :param self: Description
        :return: Description
        :rtype: str
        """
        return self._description

    @property
    def module_args(self) -> Dict[str, ModuleArg]:
        """
        Docstring for module_args
        
        :param self: Description
        :return: Description
        :rtype: Dict[str, ModuleArg]
        """
        return self._module_args

    # @property
    # def message_queue(self) -> Optional[Queue]:
    #     return self._message_queue

    # @message_queue.setter
    # def message_queue(self, queue: Queue) -> None:
    #     self._message_queue = queue

    @final
    def set_param(self, key: str, val: str) -> None:
        """
        Docstring for set_param
        
        :param self: Description
        :param key: Description
        :type key: str
        :param val: Description
        :type val: str
        """
        if key not in self._module_args:
            raise KeyError(f"Unknown option {key}")

        try:
            self._options[key] = self._module_args[key].category(val)
        except Exception as e:
            raise ValueError() from e

    @final    
    def get_param(self, key) -> Any:
        """
        Docstring for get_param

        :param self: Description
        :param key: Description
        """
        if key not in self._module_args:
            raise KeyError(f"Unknown option '{key}'")

        return self._options.get(key)

    @final
    def get_settings(self) -> Dict[str, Any]:
        """
        Docstring for get_current_settings
        
        :param self: Description
        :return: Description
        :rtype: Dict[str, Any]
        """
        settings: Dict[str, Any] = {}
        for name, _ in self._module_args.items():
            current_value: Any = self._options.get(name, None)
            settings[name] = current_value

        return settings

    @final    
    def validate(self) -> None:
        """
        Docstring for validate
        
        :param self: Description
        """
        missing_args: List[str] = []

        for name, arg in self._module_args.items():
            if arg.is_required and self._options.get(name) is None:
                missing_args.append(name)

        if missing_args:
            raise ValueError(f"Missing required options: {', '.join(missing_args)}")

    def run(self):
        """
        Docstring for run
        
        :param self: Description
        """
        # TODO: perform run logging
        raise NotImplementedError("Module must implement run()")
