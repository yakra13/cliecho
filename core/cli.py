import shlex
from pathlib import Path
from typing import Optional
from module_loader import ModuleLoader
from dispatcher import Dispatcher
from module_base import ModuleBase

class CLI:
    _dispatcher: Dispatcher

    def __init__(self, dispatcher: Dispatcher):
        self._dispatcher = dispatcher

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
