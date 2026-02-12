"""
"""
import readline
import shlex
import signal
import sys
import threading
import time
from queue import Queue
from threading import Event, Lock
from typing import Callable, Optional, List, Dict, Sequence

from core.command_registry import CommandNode, build_command_registry
# from core.completer import Completer
from core.dispatcher import Dispatcher
from core.module_loader import ModuleLoader
# from core.output_formatter import format_list_as_grid
from core.util.singleton import Singleton

from shared.formatter import format_list_as_grid
from shared.module_base import ModuleBase
from shared.module_logger import LOGGER

class CLIManager(Singleton):
    """
    Manages IO for the terminal.
    """
    def _init_once(self, *args, **kwargs) -> None:
        self._io_lock = threading.Lock()
        self._signal_interrupted = False

        signal.signal(signal.SIGINT, self._handle_interrupt)

        return super()._init_once(*args, **kwargs)

    def _handle_interrupt(self, signum, frame) -> None:
        self._signal_interrupted = True
        # To allow a "hard" exit on second press:
        # signal.signal(signal.SIGINT, signal.SIG_DFL)


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
        message = format_list_as_grid(ModuleLoader().get_modules_list())
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
        Dispatcher().set_param(args[0], args[1])
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
        current_module = Dispatcher().current_module

        if current_module:
            module_name = current_module.name or "unknown module"
            Dispatcher().set_current_module(None)
            LOGGER.console_raw(f"Exited {module_name}")
            return

        # TODO: inform run() we are exiting
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

        # TODO: auto name function handlers
        cmd = "handle_" + cmd.replace(' ', '_')
        LOGGER.console_raw(f"'{cmd}' is the auto named function name")

        # Should be valid command
        func = self._resolve_handler(node)
        if func:
            # args handled by function
            func(args)
        else:
            # TODO: misspelled function name or not implemented from the command registry
            LOGGER.console_debug(f"Handler '{node.handler}' is not implemented.")

    def run(self) -> None:
        
        while True:
            # Check job threads and update
            Dispatcher().poll_jobs()

            if self._signal_interrupted:
                # TODO: Ctrl+C was pressed. Handle it accordingly based on state
                # Reset signal interrupt flag
                self._signal_interrupted = False

                # TODO: watch command, follows a specified job and immediately prints its queue as its filled
                # ctrl c should exit the watch and return that job to standard queue display

            try:
                user_input = input(self.get_prompt())

                tokens: List[str] = self.tokenize(user_input)
                # TODO: update handle_command to return a 'command response'
                # for example handle_exit returns a response to exit to program
                # if it is not exiting the current module
                # we handle that response here so we can do clean up
                self.handle_command(tokens)
            except EOFError:
                sys.stdout.write('\n')
                sys.stdout.flush()
                # TODO: ctrl D with empty buffer will hit this exception block
                # if the buffer is not empty we dont seem to hit this block
                continue
            # except KeyboardInterrupt:
                # TODO: sig
                print("INTERRUPT STILL CAUGHT")
                # TODO: what happens if you ctrl c while handling commands?
                # TODO: check context, are we using a module? then back out
                # TODO: not in a module prep for exit, check running jobs
                # inform user and wait for them to complete?
                # TODO: what if they ctrl c during that time?
                break # continue
                # TODO: we will have a return somewhere. possible some 'exit code' too






# NOTE: disable ctrl c:
'''
import signal
import time

# Ignore SIGINT
original_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)

print("Critical work starting... Ctrl+C is disabled.")
time.sleep(5)  # This cannot be interrupted by Ctrl+C
print("Critical work done.")

# Restore original behavior
signal.signal(signal.SIGINT, original_handler)
'''
# NOTE: block ctrl c and consume it when ready
'''
import signal

# Block SIGINT
signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT})

# ... perform sensitive operations ...

# Unblock SIGINT (The exception will be raised immediately here if Ctrl+C was pressed)
signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGINT})
'''
# NOTE: custom handler
'''
import signal

class App:
    def __init__(self):
        self.interrupted = False
        signal.signal(signal.SIGINT, self.handle_interrupt)

    def handle_interrupt(self, signum, frame):
        print("\n[Soft Interrupt] Handling... (Press again to force quit)")
        self.interrupted = True
        # To allow a "hard" exit on second press:
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    def run_job(self):
        for i in range(10):
            if self.interrupted:
                print("Job halted by user.")
                self.interrupted = False # Reset flag for next job
                return 
            print(f"Working... {i}")
            time.sleep(1)

App().run_job()
'''