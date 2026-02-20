
from __future__ import annotations
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict

from .types import ConverterFn

if TYPE_CHECKING:
	from .config import BaseConfig

default_converters: Dict[type, ConverterFn] = {}

def register(conv_type: type):
	def decorator(fn: ConverterFn) -> ConverterFn:
		default_converters[conv_type] = fn
		return fn
	return decorator

@register(bool)
def _convert_bool(_: BaseConfig, value: str) -> bool:
	v = value.strip().lower()
	
	if v in {"1", "true", "yes", "on"}:
		return True
	
	if v in {"0", "false", "no", "off"}:
		return False
	
	raise ValueError(f"Invalid boolean: {value}")

@register(Path)
def _convert_path(_: BaseConfig, value: str) -> Path:
	return Path(value).expanduser().resolve()

# # @register(Enum)
# def _convert_enum(_: BaseConfig, value: str) -> Enum:
# 	try:
# 		ivalue = int(value)
		
#     except ValueError:
# 		return enum_type[value.upper()]

# 	return Enum()

def enum_converter(enum_type: type[Enum]) -> ConverterFn:
	"""
	Factory returning a converter for any Enum.
	"""

	lookup: Dict[str, Enum] = { member.name.lower(): member for member in enum_type }

	def convert(_: BaseConfig, value: str) -> Enum:
		value = value.strip()

		try:
			# allow numeric values
			return enum_type(int(value))
		except ValueError:
			pass
		
		try:
			return enum_type[value]
			# allow names
		except KeyError:
			raise ValueError(f"Invalid value '{value}' for enum {enum_type.__name__}")

	return convert