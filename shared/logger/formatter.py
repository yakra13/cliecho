from log_event import EventLog


class Formatter:
	def format(self, event: EventLog) -> str:
		return '' # TODO

class JsonFormatter(Formatter):
	def format(self, event: EventLog) -> str:
		import json
		return json.dumps(event.to_dict(), separators=(',', ':'))

class ConsoleFormatter(Formatter):
	def format(self, event: EventLog) -> str:
		return event.message