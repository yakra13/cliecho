import getpass
import socket
from datetime import datetime, timezone
from enum import Enum, auto
from dispatcher import Dispatcher
from typing import Any

class LogLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    # TODO: Special Log levels

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._dispatcher = Dispatcher()

    def _log(self, log_level: LogLevel, message: str):
        log_entry: dict = {}
        log_entry["timestamp"] = datetime.now(timezone.utc)
        log_entry["type"] = log_level.name
        log_entry["username"] = getpass.getuser()
        log_entry["hostname"] = socket.gethostname()

        # If a module is in use get its information
        current_module = self._dispatcher.current_module()

        if current_module:
            log_entry["module"]["name"] = current_module.name

            module_settings: dict[str, Any]= {}
            # Get the module option name and its current value
            for name, data in current_module.get_current_settings().items():
                # data contains a tuple [ModuleArg, Any]
                module_settings[name] = data[1]
        
            log_entry["module"]["options"] = module_settings

        log_entry["message"] = message

        # TODO: do something with the log info based on level
        # All logs go to file as json
        # log messages go to terminal, color coded
        # TODO: integration with Queue core <-> module communication?
        # Should probably occur in the Queue consumer in the core


    def warn(self, message: str) -> None:
        self._log(LogLevel.WARNING, message)

    def info(self, message: str) -> None:
        self._log(LogLevel.INFO, message)

    def err(self, message: str) -> None:
        self._log(LogLevel.ERROR, message)