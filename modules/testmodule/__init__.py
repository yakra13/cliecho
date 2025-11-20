from core.module_base import ModuleBase

class TestModule(ModuleBase):

    def run(self):
        # TODO: module implementation
        print(self.module_args.items())
