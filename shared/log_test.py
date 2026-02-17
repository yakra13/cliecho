from pathlib import Path
from typing import Any, Dict
from logger import Log, Console, ConsoleLog, LogConfig
from logger.logger import logging_context, event_queue
from logger.context import ModuleContext
# from logger.handler import FileHandler, ConsoleHandler
# from logger.formatter import JsonFormatter, ConsoleFormatter

# configure_logger(FileHandler(JsonFormatter(), Path("/logs")),
# 				 ConsoleHandler(ConsoleFormatter()))


 # Bind context for logging (standalone mode)
# context: ModuleContext = ModuleContext(
# 	name=mod.name if hasattr(mod, "name") else "NewTestModule",
# 	options=mod.get_settings() if hasattr(mod, "get_current_settings") else {}
# )

# with module_logging_context(context):
#     LOGGER.log_info("Begin Execution")
#     mod.run()




# LogConfig.console_formatter(SomeFormatter())
mod_options: Dict[str, Any] = {
	'a': '1',
	'b': '2',
	'c': '3'
	}
context: ModuleContext = ModuleContext("Some Name", mod_options)

with logging_context(context):
	Console.info("just to the console")
	Log.warn("just to the log file")
	ConsoleLog.error("To both at the same time")
	#mod.run() # execute

