# from pathlib import Path
# from typing import Final

from core.interface_manager import InterfaceManager
# from core.dispatcher import Dispatcher
# from shared.module_base import ModuleBase
# from core.module_loader import ModuleLoader


def main() -> None:
    cli = InterfaceManager()

    # TODO: handle core args


    # cli.SetVerbosity()
    # cli.SetFormat()
    cli.run()

if __name__ == "__main__":
    main()