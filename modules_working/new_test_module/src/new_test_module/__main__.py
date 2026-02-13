from importlib.resources import files
from shared.module_logger import module_logging_context, LOGGER, logging_context
from shared.module_context import ModuleContext
from . import NewTestModule

def main():
    mod = NewTestModule()

    # command line arg parsing

    # mod.validate()

    # Bind context for logging (standalone mode)
    context: ModuleContext = ModuleContext(
        name=mod.name if hasattr(mod, "name") else "NewTestModule",
        options=mod.get_settings() if hasattr(mod, "get_current_settings") else {}
    )

    # with module_logging_context(context):
    #     LOGGER.log_info("Begin Execution")
    #     mod.run()

    with logging_context(module_name=context.name,
                         module_options=context.options,):
        LOGGER.log_info("Begin execution")
        mod.run()

def show_help():
    readme = files("new_test_module").joinpath("README.md").read_text(encoding="utf-8")
    print(readme)

if __name__ == '__main__':
    main()
