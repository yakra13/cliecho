"""
Docstring for core.dispatcher
"""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Any, Optional, Type, Dict, List

from core.exceptions import NoModuleError
from core.module_loader import ModuleLoader, ModulePreset
from core.output_formatter import format_module_settings, format_show_modules

from core.util.singleton import Singleton
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

class Dispatcher(Singleton):
    """
    Docstring for Dispatcher
    """
    _loaded_modules: Dict[str, ModuleBase]
    _current_module: Optional[ModuleBase]
    _running_jobs: Dict[str, Job]
    _completed_jobs: Dict[str, List[str]]
    _job_log: Dict[str, List[str]]
    _exec_in_thread: bool
    _presets: List[ModulePreset]

    def _init_once(self, *args, **kwargs):
        self._loaded_modules = {}
        self._current_module = None
        self._running_jobs   = {}
        self._completed_jobs = {}
        self._job_log        = {}
        self._exec_in_thread = True
        self._presets        = []

    def _run_in_main(self) -> str:
        """Run current module in main thread."""
        module: Optional[ModuleBase] = self._current_module

        if module is None:
            raise NoModuleError()
            # return # TODO

        module.run()

    def _run_in_thread(self) -> str:
        module: Optional[ModuleBase] = self._current_module

        if module is None:
            raise NoModuleError()
            # return # TODO

        job_id: str = str(uuid.uuid4())

        event_queue: Queue = Queue()

        module_context: ModuleContext = ModuleContext(name=module.name,
                                                      options=module.get_settings())

        def run_module_thread():
            with module_event_queue(event_queue), module_logging_context(module_context):
                module.run()

        t = threading.Thread(target=run_module_thread)

        self._running_jobs[job_id] = Job(job_id, t, module, event_queue)

        t.start()

        return job_id

    def _cmd_show(self, args: List[str]) -> str:
        modules = ModuleLoader().get_modules_list()

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
            raise NoModuleError()

        # TODO: extract param, and value(s)
        # validate values
        try:
            module.set_param('', '') # TODO
        except (KeyError, ValueError) as e:
            return f"Error string {e}" # TODO

        return f"Set {args[0]} to '{args[1]}'" # TODO

    def has_running_jobs(self) -> bool:
        """Check if any jobs are currently running."""
        return bool(self._running_jobs)

    def update_module_presets(self) -> None:
        if self._current_module is None:
            self._presets.clear()
            return

        self._presets = ModuleLoader().discover_presets(self._current_module.name)

    def set_current_module(self, module_name: str | None) -> None:
        """
        Docstring for set_current_module
        
        :param self: Description
        :param module_name: Description
        :type module_name: str
        """
        if module_name is None:
            self._current_module = None
            self.update_module_presets()
            return

        # USE MODULE
        if not self._loaded_modules.get(module_name):
            # module not loaded
            module: Type[ModuleBase] = ModuleLoader().load(module_name)
            try:
                self._loaded_modules[module_name] = module()
            except RuntimeError:
                # TODO: log and inform user selected module could not be loaded
                # Pass up config.yml not found
                return

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
            raise NoModuleError()

        return format_module_settings(self._current_module.get_settings())

    def poll_jobs(self) -> None:
        """Polls running jobs, consumes their message queues and close finished jobs."""
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

    def run_module(self) -> str:
        """ """
        message: str = ""
        try:
            if self._exec_in_thread:
                message = self._run_in_thread()
            else:
                return self._run_in_main()

        except NoModuleError as e:
            message = str(e)

        return message

    def get_presets_list(self) -> List[str]:
        """Docstring for get_presets_list"""
        if self._current_module is None:
            raise NoModuleError()

        lines: List[str] = []

        for preset in self._presets:
            name = preset.get('preset_name', '<No Name>')
            desc = preset.get('description', '<No Description>')
            lines.append(f"{name}\n\t{desc}")

        return sorted(lines)

    def get_preset_info(self, preset_name: str) -> str:
        """
        Docstring for get_preset_info
        """
        if self._current_module is None:
            raise NoModuleError()

        for preset in self._presets:
            if str(preset.get('preset_name')).lower() == preset_name.lower():
                lines = [
                    f"{preset.get('preset_name', '<No Name>')}",
                    f"{preset.get('description', '<No Description>')}"
                ]

                for name, value in preset.items():
                    lines.append(f"{name} = {value}")

                return "\n".join(lines)

        raise KeyError(f"Preset {preset_name} not found.")
