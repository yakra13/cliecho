from core.module_loader import ModuleLoader
from core.module_base import ModuleBase

m = ModuleLoader()
ModuleClass = m.load("testmodule")
mod = ModuleClass()
mod.set_param("key", "value")
mod.run()