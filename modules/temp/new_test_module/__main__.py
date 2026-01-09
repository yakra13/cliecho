from importlib.resources import files
from shared.module_logger import module_logging_context, LOGGER
from shared.module_context import ModuleContext
from . import NewTestModule

def main():
    print("in dunder main main")
    mod = NewTestModule()

    # command line arg parsing

    # mod.validate()

    # Bind context for logging (standalone mode)
    context: ModuleContext = ModuleContext(
        name=mod.name if hasattr(mod, "name") else "NewTestModule",
        options=mod.get_settings() if hasattr(mod, "get_current_settings") else {}
    )

    # NOTE: no module_event_queue called so LOGGER.log functions should immediately print
    # to the console?
    with module_logging_context(context):
        LOGGER.log_info(f"Begin Execution: {context.name}")
        mod.run()

def show_help():
    readme = files("new_test_module").joinpath("README.md").read_text(encoding="utf-8")
    print(readme)

if __name__ == '__main__':
    main()
