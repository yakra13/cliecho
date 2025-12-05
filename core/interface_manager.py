import shlex
# from pathlib import Path
from typing import Optional

# from core.module_loader import ModuleLoader
from core.dispatcher import Dispatcher
from shared.module_base import ModuleBase

class InterfaceManager:
    """
    Docstring for InterfaceManager
    """
    _instance = None

    command_tree = {
        "show": {
            "modules": {},
            "options": {"requires_module": True}
        },
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._dispatcher: Dispatcher = Dispatcher()
        self._interactive: bool = True

    def _get_prompt(self) -> str:
        module: Optional[ModuleBase] = self._dispatcher.current_module()
        return f'{module.name}> ' if module else '> '

    def _parse_input(self, text: str) -> list[str]:
        try:
            return shlex.split(text)
        except ValueError:
            print("[-] Input parse error.")
            return []

    def _show_help(self, args: list[str]) -> str:
        return ''

    def run(self):
        # if self._interactive:
            
        #     curses.wrapper(self._curses_interface)
        # return
        while True:
            try:
                user_input = input(self._get_prompt())
            except (EOFError, KeyboardInterrupt):
                print()
                return

            # Skip blank lines
            if not user_input.strip():
                continue

            cmd, *args = self._parse_input(user_input)

            cmd = cmd.lower()

            # Central routing
            if cmd == "exit" or cmd == "quit":
                return
            elif cmd == "help":
                self._show_help(args)
            else:
                # Everything else gets sent to the dispatcher
                self._dispatcher.handle_command(cmd, args)

            # user_input = input(self._get_prompt())
            # show modules
            # search "*" (need tags or search name and description?)
            # help
            # use "module"
            # describe "module"
            # exit
            # > show options
            # > set "option" "value"
            # > unset "option"
            # > run
            # > info
            # > save settings "label" (store modules current settings value)
            # > show settings (shows saved settings for current module)
            # > load "label"
            # > back
        pass


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