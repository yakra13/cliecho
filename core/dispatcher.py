"""
Docstring for core.dispatcher
"""
import threading
import uuid
from dataclasses import dataclass
from queue import Empty, Queue
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
    def _init_once(self):
        self._loaded_modules: Dict[str, ModuleBase] = {}
        self._current_module: Optional[ModuleBase]  = None
        self._module_loader: ModuleLoader           = ModuleLoader()
        self._running_jobs: Dict[str, Job]          = {}
        self._completed_jobs: Dict[str, List[str]]  = {}
        self._job_log: Dict[str, List[str]]         = {}

    def _cmd_run(self) -> str:
        mod = self._current_module

        if mod is None:
            raise NoModuleSelectedError()
            # return # TODO

        job_id: str = str(uuid.uuid4())

        event_queue: Queue = Queue()

        module_context: ModuleContext = ModuleContext( name=mod.name, options=mod.get_settings())

        def run_module_thread():
            with module_event_queue(event_queue), module_logging_context(module_context):
                mod.run()

        t = threading.Thread(target=run_module_thread)

        self._running_jobs[job_id] = Job(job_id, t, mod, event_queue)

        t.start()

        return job_id

    def _cmd_show(self, args: List[str]) -> str:
        modules = self._module_loader.get_modules_list()

        return format_show_modules(modules)

    def _cmd_use(self, args: List[str]) -> str:
        try:
            self.set_current_module(args[0])
        except Exception as e:
            # TODO
            print(f"{e}")

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
        """
        Docstring for set_current_module
        
        :param self: Description
        :param module_name: Description
        :type module_name: str
        """
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

    def get_module_params(self) -> List[str]:
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

        return format_module_settings(self._current_module.get_settings())

    def poll_jobs(self) -> None:
        """
        Docstring for poll_jobs
        
        :param self: Description
        """
        finished_job_ids = []

        for job_id, job in self._running_jobs.items():
            # Get job messages
            while True:
                try:
                    msg = job.queue.get_nowait()
                except Empty:
                    break
                else:
                    self._job_log[job_id].append(msg)

            # Check if job complete
            if not job.thread.is_alive():
                finished_job_ids.append(job_id)

        # Remove completed jobs
        for job_id in finished_job_ids:
            self._running_jobs[job_id].thread.join()

            self._completed_jobs[job_id] = self._job_log.pop(job_id)

            del self._running_jobs[job_id]
