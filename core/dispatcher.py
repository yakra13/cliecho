from dataclasses import dataclass
import threading
import uuid
from queue import Queue
from typing import Optional, Type
from module_base import ModuleBase
from core.module_loader import ModuleLoader
from output_formatter import format_module_settings, format_show_modules
from core.exceptions import NoModuleSelectedError

@dataclass
class Job:
    id: str # uuid4
    thread: threading.Thread
    module: ModuleBase
    queue: Queue

class Dispatcher:
    _loaded_modules: dict[str, ModuleBase] = {}
    _current_module: Optional[ModuleBase] = None

    def __init__(self, module_loader: ModuleLoader):
        self._module_loader: ModuleLoader = module_loader
        self._jobs: dict[str, Job] = {}
        # self.module_class = module_class
        # self.instance = module_class()

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
        if self._current_module is None:
            raise NoModuleSelectedError()
            # return # TODO

        job_id: str = str(uuid.uuid4())
        progress_queue: Queue = Queue()
        self._current_module.progress_queue = progress_queue

        t = threading.Thread(target=self._current_module.run)

        self._jobs[job_id] = Job(job_id, t, self._current_module, progress_queue)

        t.start()

        return job_id
    
    def _cmd_show(self, args: list[str]) -> str:
        modules = self._module_loader.discover()

        return format_show_modules(modules)
    
    def _cmd_use(self, args: list[str]) -> str:
        try:
            self.set_current_module(args[0])
        except:
            pass
        return ""
    
    def _cmd_set_param(self, args: list[str]) -> str:
        module: Optional[ModuleBase] = self.current_module()
        if not module:
            raise NoModuleSelectedError()
        
        # TODO: extract param, and value(s)
        # validate values
        try:
            module.set_param('', '') # TODO
        except (KeyError, ValueError) as e:
            return "Error string" # TODO

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
    
    def current_module(self) -> Optional[ModuleBase]:
        return self._current_module

    def print_current_module_settings(self) -> str:
        # Get current module args and current arg settings
        if self._current_module is None:
            raise NoModuleSelectedError()
        
        return format_module_settings(self._current_module.get_current_settings())
    
    def handle_command(self, cmd: str, args: list[str]) -> str:
        return self._module_commands[cmd](args)
