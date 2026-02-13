from pathlib import Path
from logger import log_warn, console_warn, configure_logger

from logger.handler import FileHandler, ConsoleHandler
from logger.formatter import JsonFormatter, ConsoleFormatter

configure_logger(FileHandler(JsonFormatter(), Path("/logs")),
				 ConsoleHandler(ConsoleFormatter()))

log_warn("message")

console_warn("message")
