"""
Docstring for core.module_loader
"""
import sys
import importlib
import zipfile
from types import ModuleType
from pathlib import Path
from typing import Type, Final, Dict, Any, List, Optional

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
                # print(f'{name}')
                self._discovered_modules[name] = whl

    def load(self, name: str) -> Type[ModuleBase]:
        """
        Docstring for load
        
        :param self: Description
        :param name: Description
        :type name: str
        :return: Description
        :rtype: type[ModuleBase]
        """
        module_path: Optional[Path] = self._discovered_modules.get(name) # TODO: update
        
        if not module_path:
            raise RuntimeError(f"Module '{name}' not found")

        if not module_path.is_file():
            raise RuntimeError(f"Module file '{module_path}' not found")

        # insert the wheel path to system path
        whl_path = str(module_path)
        if whl_path not in sys.path:
            sys.path.insert(0, whl_path)

        module: ModuleType = importlib.import_module(name)

        for attr in dir(module):
            module_object = getattr(module, attr)

            is_instance: bool = isinstance(module_object, type)
            is_subclass: bool = issubclass(module_object, ModuleBase)

            if is_instance and is_subclass and module_object is not ModuleBase:
                self.loaded_modules[name] = module_object
                return module_object

        raise RuntimeError("No ModuleBase subclass found")
