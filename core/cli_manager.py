"""
"""
import readline
import shlex
from queue import Queue
import sys
from threading import Event, Lock
import threading
import time
from typing import Callable, Optional, List, Dict, Sequence

from core.command_registry import CommandNode, build_command_registry
from core.dispatcher import Dispatcher
from core.events import InputClosed, UserInterrupt
from core.module_loader import ModuleLoader
from core.output_formatter import format_list_as_table
from core.util.singleton import Singleton

from shared.module_base import ModuleBase
from shared.module_logger import LOGGER

class CLIManager(Singleton):
    """
    Manages IO for the terminal.
    """
    def _init_once(self, *args, **kwargs) -> None:
        self._io_lock = threading.Lock()
        return super()._init_once(*args, **kwargs)

    def get_prompt(self) -> str:
        module: Optional[ModuleBase] = Dispatcher().current_module
        return f'{module.name}> ' if module else 'RE> '

    def tokenize(self, text: str) -> List[str]:
        """ Split a string preserving quoted text. """
        try:
            return shlex.split(text)
        except ValueError:
            return []

#region Command Handlers
    def handle_show_jobs(self, args: Sequence[str]) -> None:
        """ Handle show jobs command. """
        message = Dispatcher().list_running_jobs()
        LOGGER.console_raw("Current jobs:\n" + message)

    def handle_show_modules(self, args: Sequence[str]) -> None:
        """ Handle show modules command. """
        # TODO: print out the available modules
        message = format_list_as_table(ModuleLoader().get_modules_list())
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
        # Exactly one arg as module name
        if len(args) != 1:
            # TODO: correct usage use module_name
            return

        # TODO: lower case a bunch of stuff
        if args[0] not in ModuleLoader().get_modules_list():
            # TODO: does not match an available module
            return

        try:
            # ModuleLoader().load(args[0])
            # Set current module and load if necessary
            Dispatcher().set_current_module(args[0])
        except RuntimeError as err:
            LOGGER.console_error(str(err))
        

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
        # print(f"handle exit: {args}")
        if Dispatcher().current_module:
            module_name = Dispatcher().current_module.name or "unknown module"
            Dispatcher().set_current_module(None)
            LOGGER.console_raw(f"Exited {module_name}")
            return

        # TODO: prep exit
        sys.exit(0)

        # if Dispatcher().has_running_jobs():



    def handle_help(self, args: Sequence[str]) -> None:
        """ Handle help command. """
        # TODO: handle help
        print(f"handle help: {args}")

#endregion

    def _resolve_handler(self, node: CommandNode) -> Optional[Callable[[List[str] | None], None]]:
        """ Resolve command node string hanlder name to function. """
        if node.handler:
            return getattr(self, node.handler)
        return None

    def handle_command(self, tokens: List[str]) -> None:
        """ Consumes list of string tokens and dispatches the resulting command. """
        # No text entered just return
        if not tokens:
            return

        node: Optional[CommandNode] = None
        args: Optional[List[str]]   = None
        cmd: str = ''
        # Get the current command registry
        registry: Dict[str, CommandNode] = build_command_registry()

        # Loop over each token
        for i, token in enumerate(tokens):
            if i == 0:
                # Get the root node from the command
                node = registry.get(token)
                cmd = token
            elif node:
                # Walk the command tree to find the final command
                # show modules
                #      presets
                #      jobs
                #      etc
                if token in node.children:
                    node = node.children[token]
                    cmd = ' '.join([cmd, token])
                else:
                    # Current token is not a child of the current node
                    # they are either arguments to the command or an invalid token

                    # Assign the remaining tokens to args
                    args = tokens[i:] if node else tokens
                    break

        # If no command node was found exit
        if node is None:
            LOGGER.console_raw(f"'{tokens[0]}' is not a valid command token")
            return

        # If the command requires a module in use but there is none exit
        if node.module_only and not Dispatcher().current_module:
            LOGGER.console_raw(f"'{cmd}' requires a module to be in use")
            return

        # Should be valid command
        func = self._resolve_handler(node)
        if func:
            # args handled by function
            func(args)
        else:
            # TODO: misspelled function name or not implemented from the command registry
            LOGGER.console_raw(f"DEVELOPER ERR: {node.handler} is not implemented or is spelled incorrectly." \
                               "See cli_manager.py or command_registry.py")


    def get_input(self, queue: Queue): #, io_lock: Lock, print_event: Event):
        """
        Docstring for run
        
        :param self: Description
        """
        while True:
            try:
                user_input = input(self.get_prompt())
            except EOFError:
                # Captures Ctrl+D (Linux) or Ctrl+Z + Enter (Windows)
                queue.put(InputClosed())
                break
            except KeyboardInterrupt:
                # Capture Ctrl+C
                queue.put(UserInterrupt())
                break

            queue.put(user_input)
            # print_event.wait()
            # try:
                # with io_lock:
                    # user_input = input(self._get_prompt())
                # queue.put(user_input)
            # except EOFError:
                # queue.put("__EOF__")
                # break

            # time.sleep(0.1)

