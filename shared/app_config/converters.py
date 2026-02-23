"""
converters.py

Converter utilities used by the configuration system to transform
string input values into strongly type Python objects.

Primarily used when loading configuration values from user input,
environment variables, or serialized config data.

Each converter receives the BaseConfig instance with the raw string
value and returns the converted result.


Default converters are automatically registered via the
``@register`` decorator and stored in ``default_converters``.


Default converters:
	- bool -> _convert_bool
	- Path -> _convert_path


Factories:
	- enum_converter(): creates converters for arbitrary Enum types

	
Example:

"""
from __future__ import annotations
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Dict

from .types import ConverterFn

if TYPE_CHECKING:
	from .config import BaseConfig

default_converters: Dict[type, ConverterFn] = {}

def register(conv_type: type):
	"""
	Automatically adds converter function to default_converters.
	"""
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
	return Path(value).expanduser().resolve(strict=False)

def enum_converter(enum_type: type[Enum]) -> ConverterFn:
	"""
	Factory returning a converter for any Enum.

	**Supports:**
		- *numeric values*	`1`
		- *enum names*		`EXAMPLE`
		- *case-insensitive*	`example`
		- *values as str*		`"1"`
	"""
	name_lookup: Dict[str, Enum] = {
		member.name.lower(): member for member in enum_type
	}

	def convert(_: BaseConfig, value: str) -> Enum:
		value: str = value.strip()

		# Numeric value conversion
		try:
			return enum_type(int(value))
		except (ValueError, TypeError):
			pass

		# Case-insensitive name match
		key = value.lower()

		if key in name_lookup:
			return name_lookup[key]

		valid_values = ', '.join(e.name.lower() for e in enum_type)

		raise ValueError(f"Invalid value '{value}' for enum {enum_type.__name__}. "
				   		 f" Valid values: {valid_values}")

	return convert
