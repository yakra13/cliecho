from pathlib import Path
from module_loader import ModuleLoader
from dispatcher import Dispatcher

def run():
    loader = ModuleLoader(Path("modules"))

    