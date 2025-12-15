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
from typing import Callable, Optional, List, Dict, Sequence

# from core.module_loader import ModuleLoader
# from core.completer import Completer
from core.command_registry import CommandRegistry, CommandNode
from core.dispatcher import Dispatcher
# from core.module_loader import ModuleLoader
from core.module_loader import ModuleLoader
from core.output_formatter import format_show_modules
from shared.module_base import ModuleBase
from core.util.singleton import Singleton

class InterfaceManager(Singleton):
    """
    Docstring for InterfaceManager
    """
    def _init_once(self, *args, **kwargs) -> None:
        return super()._init_once(*args, **kwargs)

    def _get_prompt(self) -> str:
        module: Optional[ModuleBase] = Dispatcher().current_module
        return f'{module.name}> ' if module else '> '

    def tokenize(self, text: str) -> List[str]:
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

#region Command Handlers

    def handle_show_modules(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_show_modules
        
        :param self: Description
        """
        # TODO: print out the available modules
        print(f"handle show modules: {args}")
        # module_loader = ModuleLoader()
        print(ModuleLoader().get_modules_list())

    def handle_show_options(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_show_options
        
        :param self: Description
        """
        # TODO: show current modules options/settings
        print(f"handle show options: {args}")

    def handle_show_presets(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_show_presets
        
        :param self: Description
        """
        # TODO: show list of available presets for current module
        print(f"handle show presets: {args}")

    def handle_info(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_info
        
        :param self: Description
        """
        # TODO: show info on specified module or current module if no args
        print(f"handle info: {args}")

    def handle_use(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_use
        
        :param self: Description
        :param args: Description
        :type args: List[str]
        """
        # TODO: set current module
        print(f"handle use: {args}")

    def handle_set(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle current module set param value
        print(f"handle set: {args}")

    def handle_preset_save(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle current module preset save
        print(f"handle preset save: {args}")

    def handle_preset_load(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle current module preset load
        print(f"handle preset load: {args}")

    def handle_exit(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle exit/current module exit
        print(f"handle exit: {args}")

    def handle_help(self, args: Sequence[str]) -> None:
        """
        Docstring for handle_set
        
        :param self: Description
        :param args: Description
        :type args: Sequence[str]
        """
        # TODO: handle help
        print(f"handle help: {args}")

#endregion

    def _resolve_handler(self, node: CommandNode) -> Optional[Callable[[List[str]], None]]:
        if node.handler:
            return getattr(self, node.handler)
        return None

    def handle_command(self, tokens: List[str]) -> None:
        if not tokens:
            return
        
        node: Optional[CommandNode] = None
        registry: Dict[str, CommandNode] = CommandRegistry.build()
        dispatcher: Dispatcher = Dispatcher()

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
            if node.module_only and not dispatcher.current_module:
                # TODO: No module in use
                return

            args = tokens[i + 1:] if node else tokens

            if node:
                func = self._resolve_handler(node) #node.handler(args)
                if func:
                    func(args)
                else:
                    # TODO: misspelled function name or not implemented
                    pass
            else:
                # TODO: incomplete command
                pass


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