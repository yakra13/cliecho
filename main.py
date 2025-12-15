"""
TODO: docstring
"""
from core.interface_manager import InterfaceManager
from core.module_loader import ModuleLoader

def main() -> None:
    """
    Docstring for main
    """
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
