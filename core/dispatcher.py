"""
Docstring for core.dispatcher
"""
import threading
import uuid
from dataclasses import dataclass
from queue import Queue
from typing import Optional, Type, Dict, List

from core.exceptions import NoModuleSelectedError
from core.module_loader import ModuleLoader
from core.output_formatter import format_module_settings, format_show_modules

from shared.module_base import ModuleBase
from shared.module_context import ModuleContext
from shared.module_logger import module_event_queue, module_logging_context

@dataclass
class Job:
    """
    Docstring for Job
    """
    id: str # uuid4
    thread: threading.Thread
    module: ModuleBase
    queue: Queue

class Dispatcher:
    """
    Docstring for Dispatcher
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._loaded_modules: Dict[str, ModuleBase] = {}
        self._current_module: Optional[ModuleBase] = None
        self._module_loader: ModuleLoader = ModuleLoader()
        self._jobs: Dict[str, Job] = {}

        self._global_commands = {
            "show": self._cmd_show,
            # "search": self.cmd_search,
            # "use": self.cmd_use,
            # "describe": self.cmd_describe,
            # "back": self.cmd_back,
            # "kill": self._cmd_kill,
        }

        self._module_commands = {
            "set": self._cmd_set_param,
            # "unset": self._cmd_unset_param,
            "run": self._cmd_run,
            # "info": self.cmd_info,
            # "save": self.cmd_save,
            # "load": self.cmd_load,
        }

    def _cmd_run(self) -> str:
        if self.current_module is None:
            raise NoModuleSelectedError()
            # return # TODO

        job_id: str = str(uuid.uuid4())
        event_queue: Queue = Queue()
        module_context: ModuleContext = ModuleContext(
            name=self._current_module.name,
            options=self._current_module.get_current_settings()
        )

        def run_module_thread():
            with module_event_queue(event_queue), module_logging_context(module_context):
                self._current_module.run()
        # self._current_module.message_queue = progress_queue

        t = threading.Thread(target=run_module_thread)

        self._jobs[job_id] = Job(job_id, t, self._current_module, event_queue)

        t.start()

        return job_id

    def _cmd_show(self, args: List[str]) -> str:
        modules = self._module_loader.discover()

        return format_show_modules(modules)

    def _cmd_use(self, args: List[str]) -> str:
        try:
            self.set_current_module(args[0])
        except:
            pass
        return ""

    def _cmd_set_param(self, args: List[str]) -> str:
        module: Optional[ModuleBase] = self.current_module
        if not module:
            raise NoModuleSelectedError()

        # TODO: extract param, and value(s)
        # validate values
        try:
            module.set_param('', '') # TODO
        except (KeyError, ValueError) as e:
            return f"Error string {e}" # TODO

        return f"Set {args[0]} to '{args[1]}'" # TODO

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

    @property
    def current_module(self) -> Optional[ModuleBase]:
        """
        Docstring for current_module
        
        :param self: Description
        :return: Description
        :rtype: ModuleBase | None
        """
        return self._current_module

    def get_current_module_params(self) -> List[str]:
        """
        Docstring for get_current_module_params
        
        :param self: Description
        :return: Description
        :rtype: List[str] | None
        """
        if not self._current_module:
            return []

        return list(self._current_module.module_args.keys())

    def print_current_module_settings(self) -> str:
        """
        Docstring for print_current_module_settings
        
        :param self: Description
        :return: Description
        :rtype: str
        """
        # Get current module args and current arg settings
        if self._current_module is None:
            raise NoModuleSelectedError()

        return format_module_settings(self._current_module.get_current_settings())

    def handle_command(self, cmd: str, args: List[str]) -> str:
        """
        Docstring for handle_command
        
        :param self: Description
        :param cmd: Description
        :type cmd: str
        :param args: Description
        :type args: list[str]
        :return: Description
        :rtype: str
        """
        return self._module_commands[cmd](args)
