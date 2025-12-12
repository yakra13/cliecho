"""
Docstring for core.module_loader
"""
import sys
import importlib
import zipfile
from types import ModuleType
from pathlib import Path
from typing import Type, Final, Dict, Any, List

from shared.module_base import ModuleBase

MODULE_DIR: Final[Path] = Path("dist")#Path("modules")

class ModuleLoader:
    """
    Docstring for ModuleLoader
    """
    def __init__(self):
        self.modules_path: Path = MODULE_DIR
        self.loaded_modules: Dict[str, Type[ModuleBase]] = {}
        self._discovered_modules: Dict[str, Path] = {}

    # @property
    # def discovered_modules(self) -> Dict[str, Path]:
    #     return self._discovered_modules

    def get_modules_list(self) -> List[str]:
        return list(self._discovered_modules.keys())

    def discover(self) -> None:
        """
        Docstring for discover
        
        :param self: Description
        """
        wheel_files = MODULE_DIR.glob("*.whl")

        # discovered = {}

        for whl in wheel_files:
            with zipfile.ZipFile(whl, "r") as zf:
                meta_file = next((f for f in zf.namelist() if f.endswith("METADATA")), None)
                if not meta_file:
                    continue

                meta = zf.read(meta_file).decode("utf8")
                name = "UNABLE TO EXTRACT NAME" # TODO: better failing
                print(f'{meta}')
                for line in meta.splitlines():
                    s = line.strip()
                    if s.startswith("Name:"):
                        name = s.split()[1].strip()
                # name = meta.splitlines()[1].replace("Name: ", "").strip()
                print(f'{name}')
                self._discovered_modules[name] = whl
                # {
                #     "file": whl,
                #     "module_name": name,
                # }

        
        # return discovered

    def load(self, name: str) -> Type[ModuleBase]:
        """
        Docstring for load
        
        :param self: Description
        :param name: Description
        :type name: str
        :return: Description
        :rtype: type[ModuleBase]
        """
        info = self.discover().get(name) # TODO: update
        if not info:
            raise RuntimeError(f"Module '{name}' not found")

        whl_path = str(info["file"])
        sys.path.append(whl_path)

        module: ModuleType = importlib.import_module(info["module_name"])

        for attr in dir(module):
            module_object = getattr(module, attr)

            is_instance: bool = isinstance(module_object, type)
            is_subclass: bool = issubclass(module_object, ModuleBase)

            if is_instance and is_subclass and module_object is not ModuleBase:
                self.loaded_modules[name] = module_object
                return module_object

        raise RuntimeError("No ModuleBase subclass found")
