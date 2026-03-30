from logging import FileHandler, StreamHandler
from .formatters import JsonFormatter

def file_handler(filename: str):
    h = FileHandler(filename)
    h.setFormatter(JsonFormatter())
    return h

def console_handler():
    h = StreamHandler()
    h.setFormatter(JsonFormatter())
    return h