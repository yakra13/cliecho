import sys
import importlib
from types import ModuleType
import zipfile
from pathlib import Path
from typing import Type
from module_base import ModuleBase

MODULE_DIR = Path("modules")

class ModuleLoader:
    def __init__(self, modules_path: Path):
        self.modules_path = modules_path
        self.loaded_modules = {}

    def discover(self):
        wheel_files = MODULE_DIR.glob("*.whl")

        discovered = {}

        for whl in wheel_files:
            with zipfile.ZipFile(whl, "r") as zf:
                meta_file = next((f for f in zf.namelist() if f.endswith("METADATA")), None)
                if not meta_file:
                    continue

                meta = zf.read(meta_file).decode("utf8")
                name = meta.splitlines()[0].replace("Name: ", "").strip()

                discovered[name] = {
                    "file": whl,
                    "module_name": name,
                }

        return discovered

    def load(self, name: str) -> Type[ModuleBase]:
        info = self.discover().get(name)
        if not info:
            raise RuntimeError(f"Module '{name}' not found")
        
        whl_path = str(info["file"])
        sys.path.append(whl_path)

        module: ModuleType = importlib.import_module(info["module_name"])
        
        for attr in dir(module):
            modobj = getattr(module, attr)
            if isinstance(modobj, type) and issubclass(modobj, ModuleBase) and modobj is not ModuleBase:
                self.loaded_modules[name] = modobj
                return modobj

        raise RuntimeError("No ModuleBase subclass found")
