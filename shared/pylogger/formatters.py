import logging
import json
import time
from .context import get_context

class JsonFormatter(logging.Formatter):
	"""JSON formatter that automatically injects context"""

	def format(self, record: logging.LogRecord) -> str:
		ctx = get_context()
		log_entry = {
			"timestamp": time.time(),
			"level": record.levelname,
			"message": record.getMessage(),
		}

		# Include context
		if ctx:
			log_entry.update(ctx)

		# Include structured extra data
		if hasattr(record, "data"):
			log_entry.update(record.data)

		return json.dumps(log_entry)