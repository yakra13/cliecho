"""
"""
import shlex
from queue import Queue
from threading import Event, Lock
import time
from typing import Callable, Optional, List, Dict, Sequence

from core.command_registry import CommandNode, build_command_registry
from core.dispatcher import Dispatcher
from core.module_loader import ModuleLoader
from core.output_formatter import format_show_modules
from core.util.singleton import Singleton

from shared.module_base import ModuleBase
from shared.module_logger import LOGGER

class CLIManager(Singleton):
    """
    Manages IO for the terminal.
    """
    def _init_once(self, *args, **kwargs) -> None:
        return super()._init_once(*args, **kwargs)

    def _get_prompt(self) -> str:
        module: Optional[ModuleBase] = Dispatcher().current_module
        return f'{module.name}> ' if module else 'RE> '

    def tokenize(self, text: str) -> List[str]:
        """ Split a string preserving quoted text. """
        try:
            return shlex.split(text)
        except ValueError:
            return []

#region Command Handlers

    def handle_show_modules(self, args: Sequence[str]) -> None:
        """ Handle show modules command. """
        # TODO: print out the available modules
        message = format_show_modules(ModuleLoader().get_modules_list())
        LOGGER.console_raw("Available modules:\n" + message)

    def handle_show_options(self, args: Sequence[str]) -> None:
        """ Handle show options command. """
        # TODO: show current modules options/settings
        print(f"handle show options: {args}")

    def handle_show_presets(self, args: Sequence[str]) -> None:
        """ Handle show presets command. """
        # TODO: show list of available presets for current module
        print(f"handle show presets: {args}")

    def handle_info(self, args: Sequence[str]) -> None:
        """ Handle info command. """
        # TODO: show info on specified module or current module if no args
        print(f"handle info: {args}")

    def handle_use(self, args: Sequence[str]) -> None:
        """ Handle use command. """
        # TODO: set current module
        print(f"handle use: {args}")

    def handle_run(self, args: Sequence[str]) -> None:
        """Handle run command."""
        Dispatcher().run_module()

    def handle_set(self, args: Sequence[str]) -> None:
        """ Handle set command. """
        # TODO: handle current module set param value
        print(f"handle set: {args}")

    def handle_preset_save(self, args: Sequence[str]) -> None:
        """ Handle preset save command. """
        # TODO: handle current module preset save
        print(f"handle preset save: {args}")

    def handle_preset_load(self, args: Sequence[str]) -> None:
        """ Handle preset load command. """
        # TODO: handle current module preset load
        print(f"handle preset load: {args}")

    def handle_exit(self, args: Sequence[str]) -> None:
        """ Handle exit command. """
        # TODO: handle exit/current module exit
        print(f"handle exit: {args}")
        if Dispatcher().current_module:
            module_name = Dispatcher().current_module.name or "unknown module"
            Dispatcher().set_current_module(None)
            LOGGER.console_raw(f"Exited {module_name}")
            return

        # TODO: 

        # if Dispatcher().has_running_jobs():


    def handle_help(self, args: Sequence[str]) -> None:
        """ Handle help command. """
        # TODO: handle help
        print(f"handle help: {args}")

#endregion

    def _resolve_handler(self, node: CommandNode) -> Optional[Callable[[List[str]], None]]:
        """ Resolve command node string hanlder name to function. """
        if node.handler:
            return getattr(self, node.handler)
        return None

    def handle_command(self, tokens: List[str]) -> None:
        """ Consumes list of string tokens and dispatches the resulting command. """
        if not tokens:
            return

        node: Optional[CommandNode] = None
        registry: Dict[str, CommandNode] = build_command_registry()

        for i, token in enumerate(tokens):
            if i == 0:
                node = registry.get(token)
            else:
                if node and token in node.children:
                    node = node.children[token]
                else:
                    break

            if node is None:
                # TODO: Invalid command "{' '.join(tokens[:i+1])}"
                return

            # Check if its a module command and there is a module in use
            if node.module_only and not Dispatcher().current_module:
                # TODO: No module in use
                return

            args = tokens[i + 1:] if node else tokens
            if node:
                # Find the matching handler function from the command node
                func = self._resolve_handler(node)
                if func:
                    func(args)
                else:
                    # TODO: misspelled function name or not implemented
                    LOGGER.log_error(f"{node.handler} function not found.")
            else:
                # TODO: incomplete command
                pass

    def get_input(self, queue: Queue, io_lock: Lock, print_event: Event):
        """
        Docstring for run
        
        :param self: Description
        """
        while True:
            print_event.wait()
            try:
                with io_lock:
                    user_input = input(self._get_prompt())
                queue.put(user_input)
            except EOFError:
                queue.put("__EOF__")
                break

            # time.sleep(0.1)
