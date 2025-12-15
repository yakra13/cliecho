"""
LogManager docstring
"""
import getpass
import socket
from datetime import datetime, timezone
from typing import Any, Dict
from shared.log_types import LogLevel, Event
from core.dispatcher import Dispatcher


class LogManager:
    """
    Docstring for Logger
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._dispatcher = Dispatcher()

    def _log(self, log_level: LogLevel, message: str):
        event: Event = Event(message=message, log_level=log_level)
        log_entry: dict = {}
        log_entry["timestamp"] = datetime.now(timezone.utc)
        log_entry["type"] = log_level.name
        log_entry["username"] = getpass.getuser()
        log_entry["hostname"] = socket.gethostname()

        # If a module is in use get its information
        current_module = self._dispatcher.current_module

        if current_module:
            log_entry["module"]["name"] = current_module.name

            module_settings: Dict[str, Any]= {}
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