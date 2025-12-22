#!/usr/bin/env python3
import os
import sys
import textwrap

TEMPLATE_INIT_PY = '''\
"""
TODO: Module Docstring
"""
from shared.module_base import ModuleBase

class {classname}(ModuleBase):
    """
    TODO: class docstring
    """
    def run(self):
        super.run()
        # TODO: Implementation
        raise NotImplementedError("Module must implement run()")
'''

TEMPLATE_MAIN_PY = '''\
from importlib.resources import files
from shared.module_logger import module_logging_context, LOGGER
from shared.module_context import ModuleContext
from . import {classname}

def main():
    mod = {classname}()

    # command line arg parsing

    # mod.validate()

    # Bind context for logging (standalone mode)
    context: ModuleContext = ModuleContext(
        name=mod.name if hasattr(mod, "name") else "{classname}",
        options=mod.get_current_settings() if hasattr(mod, "get_current_settings") else {{}}
    )

    with module_logging_context(context):
        LOGGER.log_info("Begin Execution")
        mod.run()

def show_help():
    readme = files("{modulename}").joinpath("README.md").read_text(encoding="utf-8")
    print(readme)

if __name__ == '__main__':
    main()
'''

TEMPLATE_CONFIG_YML = '''\
description: "{modulename} description"
arguments:
    required:
        examplerequired:
            default: "default_value"
            type: "str"
            description: "description"
            help: "help text"
            shortname: "?"

    optional:
        exampleoptional:
            type: "str"
            description: "description"
            help: "help text"
            shortname: "?"
'''
TEMPLATE_README_MD = '''\
# {modulename}
## {classname}
'''

TEMPLATE_PROJECT_TOML = '''\
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{modulename}"
version = "0.1.0"
description = "{modulename} description"
readme = "README.md"
requires-python = ">=3.8"

# Exposes: python -m {modulename}
[project.scripts]
{modulename} = "{modulename}.__main__:main"

[tool.setuptools]
package-dir = {{ "" = "." }}

[tool.setuptools.package-data]
"{modulename}" = ["config.yml", "README.md"]

[tool.setuptools.packages.find]
where = ["."]
'''

TEMPLATE_BUILD_SH = '''\
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

MODULE_NAME=$(basename "$PWD")
echo "[*] Building wheel for $MODULE_NAME using python3.8"

# Clean old build artifacts
rm -rf dist build *.egg-info

# Make sure build tools are installed
python3 -m pip install --upgrade pip setuptools wheel build

# Build the wheel
python3 -m build --wheel

echo "[+] Build complete! Wheel file(s) in dist/:"
ls -lh dist/*.whl
'''

def create_module(module_name: str) -> None:
    """
    Docstring for create_module
    
    :param module_name: Description
    :type module_name: str
    """
    base_path = os.path.join("modules_working", module_name)
    src_path = os.path.join(base_path, f"src/{module_name}")

    if os.path.exists(base_path):
        print(f"[!] Module '{module_name}' already exists.")
        return

    os.makedirs(src_path)

    class_name = ''.join(part.capitalize() for part in module_name.split('_'))

    with open(os.path.join(src_path, "__init__.py"), "w", encoding='utf8') as f:
        f.write(TEMPLATE_INIT_PY.format(classname=class_name))

    try:
        with open(os.path.join(src_path, "__main__.py"), "w", encoding='utf8') as f:
            f.write(TEMPLATE_MAIN_PY.format(classname=class_name, modulename=module_name))
    except IndexError as e:
        print(f"__main__ fail: {e}")

    # module.py where the main implementation lives
    with open(os.path.join(base_path, "pyproject.toml"), "w", encoding='utf8') as f:
        f.write(TEMPLATE_PROJECT_TOML.format(modulename=module_name))

    with open(os.path.join(base_path, "build.sh"), "w", encoding='utf8') as f:
        f.write(TEMPLATE_BUILD_SH)

    with open(os.path.join(src_path, "config.yml"), "w", encoding='utf8') as f:
        f.write(TEMPLATE_CONFIG_YML.format(modulename=module_name))

    with open(os.path.join(src_path, "README.md"), "w", encoding='utf8') as f:
        f.write(TEMPLATE_README_MD.format(classname=class_name, modulename=module_name))

    print(f"[+] Module '{module_name}' created in {base_path}/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: create_module.py <module_name>")
        sys.exit(1)

    create_module(sys.argv[1])
