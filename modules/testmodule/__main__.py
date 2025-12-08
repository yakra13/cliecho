"""
Docstring for modules.testmodule.__main__
"""
from shared.module_logger import module_logging_context, LOGGER
from shared.module_context import ModuleContext
from . import TestModule

def main():
    """
    Docstring for main
    """
    # command line arg parsing
    mod = TestModule()

    # mod.validate() # TODO: cancellation point

    # Bind context for logging (standalone mode)
    context: ModuleContext = ModuleContext(
        name=mod.name if hasattr(mod, "name") else "TestModule",
        options=mod.get_current_settings() if hasattr(mod, "get_current_settings") else {}
    )

    with module_logging_context(context):
        LOGGER.info("Begin Execution")
        mod.run()

if __name__ == '__main__':
    main()
