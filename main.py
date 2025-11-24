from pathlib import Path
from typing import Final
from core.module_loader import ModuleLoader
from core.module_base import ModuleBase
from core.cli import CLI
from core.dispatcher import Dispatcher


MODULES_PATH: Final[Path] = Path("modules") 

m = ModuleLoader(Path("modules"))
ModuleClass = m.load("testmodule")
mod = ModuleClass()
mod.set_param("key", "value")

mod.run()

def main() -> None:
    # 
    loader: ModuleLoader   = ModuleLoader(MODULES_PATH)
    dispatcher: Dispatcher = Dispatcher(loader)
    cli = CLI(dispatcher)
    # cli.SetVerbosity()
    # cli.SetFormat()
    cli.run()

if __name__ == "__main__":
    main()