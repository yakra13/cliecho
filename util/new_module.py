#!/usr/bin/env python3
import os
import sys
import textwrap

TEMPLATE_INIT_PY = '''\
from core.module_base import ModuleBase

class {classname}(ModuleBase):
    def run(self):
        super.run()
        # TODO: Implementation
        raise NotImplementedError("Module must implement run()")
'''

TEMPLATE_MAIN_PY = '''\
from . import {classname}

def main():
    mod = {classname}()

    # command line arg parsing

    # mod.validate()

    mod.run()

if __name__ == '__main__':
    main()
'''

TEMPLATE_CONFIG_YML = '''\
description: "{modulename} description"
arguments:
    required:
        examplerequired:
            description: "description"
            default: "default_value"
            help: "help text"
            shortname: "?"

    optional:
        exampleoptional:
            description: "description"
            help: "help text"
            shortname: "?"
'''

TEMPLATE_PROJECT_TOML = '''\
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{modulename}"
version = "0.1.0"
description = "{modulename} description"
readme = "README.md"
requires-python = ">=3.8"

# Exposes: python -m {modulename}
[project.scripts]
testmodule = "{modulename}.__main__:main"

[tool.setuptools]
package-dir = {{ "" = "." }}

[tool.setuptools.package-data]
"{modulename}" = ["*.yml"]
'''

def create_module(module_name: str):
    base_path = os.path.join("modules", module_name)

    if os.path.exists(base_path):
        print(f"[!] Module '{module_name}' already exists.")
        return
    
    os.makedirs(base_path)

    classname = ''.join(part.capitalize() for part in module_name.split('_'))

    with open(os.path.join(base_path, "__init__.py"), "w") as f:
        f.write(TEMPLATE_INIT_PY.format(classname=classname))
    
    with open(os.path.join(base_path, "__main__.py"), "w") as f:
        f.write(TEMPLATE_MAIN_PY.format(classname=classname))

    # module.py where the main implementation lives
    with open(os.path.join(base_path, "pyproject.toml"), "w") as f:
        f.write(TEMPLATE_PROJECT_TOML.format(modulename=module_name))

    with open(os.path.join(base_path, "config.yml"), "w") as f:
        f.write(TEMPLATE_CONFIG_YML.format(modulename=module_name))

    print(f"[+] Module '{module_name}' created in {base_path}/")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: create_module.py <module_name>")
        sys.exit(1)
    
    create_module(sys.argv[1])
