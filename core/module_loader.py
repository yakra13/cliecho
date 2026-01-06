"""
Docstring for core.module_loader
"""
import importlib
import json
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Type, Dict, List, Optional
import zipimport

from core.util.singleton import Singleton
from shared.module_base import ModuleBase
# from core.dispatcher import Dispatcher

@ dataclass
class ModulePreset():
    preset_name: str
    description: str
    values: Dict[str, Any]

class ModuleLoader(Singleton):
    """
    Docstring for ModuleLoader
    """
    _modules_path: Path
    _presets_path: Path
    _loaded_modules: Dict[str, Type[ModuleBase]]
    _discovered_modules: Dict[str, Path]

    def _init_once(self, *args, **kwargs):
        self._modules_path       = Path("modules")
        self._presets_path       = Path("presets")
        self._loaded_modules     = {}
        self._discovered_modules = {}

    def get_modules_list(self) -> List[str]:
        """Docstring for get_modules_list"""
        modules = list(self._discovered_modules.keys())
        modules.sort()
        return modules

    def discover(self) -> None:
        """Docstring for discover"""
        wheel_files = self._modules_path.glob("*.whl")

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

    def discover_presets(self, module_name: str) -> List[ModulePreset]:
        presets: List[ModulePreset] = []
        file_path: Path = self._presets_path / module_name

        with open(file_path, 'r', encoding='utf8') as file:
            data = json.load(file)

        if isinstance(data, dict):
            presets_data = [data]
        elif isinstance(data, list):
            presets_data = data
        else:
            raise ValueError(f"Unexpected format in {file_path}")

        for data in presets_data:
            name = data.pop('preset_name', '<Unnamed>')
            desc = data.pop('description', '')
            presets.append(ModulePreset(name, desc, data))

        return presets

    def load(self, name: str) -> Type[ModuleBase]:
        """Docstring for load"""
        module_path: Optional[Path] = self._discovered_modules.get(name) # TODO: update

        if not module_path:
            raise RuntimeError(f"Module '{name}' not found")

        if not module_path.is_file():
            raise RuntimeError(f"Module file '{module_path}' not found")

        # Insert the wheel path to system path
        # whl_path = str(module_path)
        # if whl_path not in sys.path:
        #     sys.path.insert(0, whl_path)
        
        extract_dir = Path(".temp_modules") / module_path.stem
        src_dir = extract_dir

        extract_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(module_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # TODO: handle src_dir errors and such
        if src_dir.is_dir() and str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))

        module: ModuleType = importlib.import_module(name)

        for attr in dir(module):
            module_object = getattr(module, attr)

            is_instance: bool = isinstance(module_object, type)
            is_subclass: bool = issubclass(module_object, ModuleBase)

            # Only create the module object if it is a subclass of ModuleBase
            if is_instance and is_subclass and module_object is not ModuleBase:
                self._loaded_modules[name] = module_object
                return module_object

        raise RuntimeError("No ModuleBase subclass found")
