from typing import Type
from module_base import ModuleBase

class Dispatcher:
    def __init__(self, module_class: Type[ModuleBase]):
        self.module_class = module_class
        self.instance = module_class()
    
    