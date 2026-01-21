
from dataclasses import dataclass
from typing import Any


@dataclass
class ArgType:
    value: str

@dataclass
class PortArg(ArgType):
    def validate(self):
        try:
            # All args start as str, perform conversion
            value = int(self.value)
        except ValueError as e:
            # TODO:
            raise ValueError from e

        if 0 > value > 65535:
            raise ValueError()

