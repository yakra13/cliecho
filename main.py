# from pathlib import Path
# from typing import Final
import readline
from typing import Optional, List
from core.interface_manager import InterfaceManager
# from core.dispatcher import Dispatcher
# from shared.module_base import ModuleBase
from core.module_loader import ModuleLoader

COMMANDS = {'show': ['modules', 'options', 'presets'],
            'use': [],
            'set': [],
            'exit': []
            }

def completer(text: str, state: int) -> Optional[str]:
    line = readline.get_line_buffer()
    parts = line.lstrip().split()

    # TODO: do this for use "module name" etc
    module_loader = ModuleLoader()
    modules: List[str] = module_loader.get_modules_list()

    # First word completion
    if len(parts) == 0 or (len(parts) == 1 and not line.endswith(" ")):
        options = [c for c in COMMANDS if c.startswith(text)]
    # Second word completion
    elif len(parts) == 1 or (len(parts) == 2 and not line.endswith(" ")):
        parent_cmd = parts[0]
        options = [c for c in COMMANDS.get(parent_cmd, []) if c.startswith(text)]
    else:
        options = []

    try:
        return options[state]
    except IndexError:
        return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

def main() -> None:

    # TODO: load stuff
    module_loader = ModuleLoader()
    module_loader.discover()
    print(module_loader.get_modules_list())

    while True:
        cmd = input("echo> ")
        print("You typed:", cmd)

    cli = InterfaceManager()

    # TODO: handle core args


    # cli.SetVerbosity()
    # cli.SetFormat()
    cli.run()

if __name__ == "__main__":
    main()