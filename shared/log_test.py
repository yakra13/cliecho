from copy import deepcopy
from pathlib import Path
from time import sleep
from typing import Any, Dict
from logger import Log, Console, ConsoleLog, LogConfig
from logger.logger import logging_context, event_queue
from logger.context import ModuleContext
from logger.formatter import Verbosity
from util.system import SystemInfo
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


# LogConfig.set_metadata(current_user=SystemInfo.get_system_username(),
# 					   current_host=SystemInfo.get_system_hostname())


LogConfig.metadata.current_user = SystemInfo.get_system_username()
LogConfig.metadata.current_host = SystemInfo.get_system_hostname()
LogConfig.metadata.custom = 5
LogConfig.metadata.whatever_you_want = "some value"


val = LogConfig.metadata.current_user
# LogConfig.file_formatter = JsonFormatter()
LogConfig.log_directory = Path("/home/joshua.ziebarth/Documents")
val2 = LogConfig.log_directory
LogConfig.verbosity = Verbosity.DEBUG
print(val)
print(val2)

# LogConfig.console_formatter(SomeFormatter())
mod_options: Dict[str, Any] = {
	'a': '1',
	'b': '2',
	'c': '3'
	}
context: ModuleContext = ModuleContext("Some_Name", mod_options)

with logging_context(context):
	Console.info("just to the console")
	Log.warn("just to the log file")
	sleep(1)
	Console.warn("console warning")
	Console.debug("console debug message")
	ConsoleLog.error("To both at the same time")
	#mod.run() # execute

