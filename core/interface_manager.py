"""
"""
# try:
# import readline
# except ImportError:
#     # Windows
#     import pyreadline3 as readline
from queue import Queue
import shlex
# from pathlib import Path
from typing import Optional, List, Dict, Sequence

# from core.module_loader import ModuleLoader
# from core.completer import Completer
from core.command_registry import CommandRegistry, CommandNode
from core.dispatcher import Dispatcher
# from core.module_loader import ModuleLoader
from shared.module_base import ModuleBase

class InterfaceManager:
    """
    Docstring for InterfaceManager
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # def __init__(self):
        # self._dispatcher: Dispatcher = Dispatcher()
        # self._interactive: bool = True

    def _get_prompt(self) -> str:
        module: Optional[ModuleBase] = Dispatcher().current_module
        return f'{module.name}> ' if module else '> '

    def parse_input(self, text: str) -> List[str]:
        """
        Docstring for parse_input
        
        :param self: Description
        :param text: Description
        :type text: str
        :return: Description
        :rtype: List[str]
        """
        try:
            return shlex.split(text)
        except ValueError:
            return []

    def _show_help(self) -> str:
        return 'TODO: help'

    def handle_show_modules(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_show_modules
        
        :param self: Description
        """
        # TODO: print out the available modules
        pass

    def handle_show_options(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_show_options
        
        :param self: Description
        """
        # TODO: show current modules options/settings
        pass

    def handle_show_presets(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_show_presets
        
        :param self: Description
        """
        # TODO: show list of available presets for current module
        pass

    def handle_info(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_info
        
        :param self: Description
        """
        # TODO: show info on specified module or current module if no args
        pass

    def handle_use(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_use
        
        :param self: Description
        :param args: Description
        :type args: List[str]
        """
        # TODO: set current module
        pass

    def handle_set(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle current module set param value
        pass

    def handle_preset_save(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle current module preset save
        pass

    def handle_preset_load(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle current module preset load
        pass

    def handle_exit(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle exit/current module exit
        pass

    def handle_help(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle help
        pass

    def handle_command(self, tokens: List[str]) -> None:
        if not tokens:
            return

        cmd, *args = tokens
        commands = CommandRegistry.build()

        if tokens[0] in commands:
            spec: CommandNode = commands[cmd]

            if spec.module_only and not Dispatcher().current_module:
                # TODO: inform no module in use
                return

            if spec.handler:
                spec.handler(args)
                return

        dispatcher = Dispatcher()

        if not dispatcher.current_module:
            # TODO: unknown command
            return

        dispatcher.handle_command(cmd, args)

    # TODO: dispatch logic for new CommandNodes????
    # def dispatch(tokens: List[str]) -> None:
    #     node = None
    #     registry = CommandRegistry.build()
    #     dispatcher = Dispatcher()

    #     for i, token in enumerate(tokens):
    #         if i == 0:
    #             node = registry.get(token)
    #         else:
    #             if node and token in node.children:
    #                 node = node.children[token]
    #             else:
    #                 break

    #         if node is None:
    #             print(f"Unknown command: {' '.join(tokens[:i+1])}")
    #             return

    #         if node.module_only and not dispatcher.current_module:
    #             print("No module in use.")
    #             return

    #     remaining_args = tokens[i+1:] if node else tokens

    #     if node and node.handler:
    #         node.handler(remaining_args)
    #     else:
    #         print("Incomplete command.")

    def get_input(self, queue: Queue):
        """
        Docstring for run
        
        :param self: Description
        """
        while True:
            try:
                # Dispatcher check Jobs/message queue

                user_input = input(self._get_prompt())
                queue.put(user_input)
            except EOFError:
                queue.put("__EOF__")
                break

# example
'''
dispatcher = Dispatcher()

cli = CLI(dispatcher)

curses.wrapper(cli.run)



def main():
    dispatcher = Dispatcher()
    dispatcher.register_module("mod", ExampleModule())

    if "--curses" in sys.argv:
        curses_cli = CursesCLI(dispatcher)
        curses.wrapper(curses_cli.run)
    else:
        std_cli = StandardCLI(dispatcher)
        std_cli.run()
'''