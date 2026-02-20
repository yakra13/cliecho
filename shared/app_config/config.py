from __future__ import annotations

import configparser
from dataclasses import Field, dataclass, field, fields
# from datetime import datetime
from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, Final, Iterable, List, Optional, Tuple, Type, get_type_hints

# from shared.validation import validate_thread_count, timestamp_format
# from shared.module_logger import EventLevel
# from shared.task import TaskMessage, TaskResult
# from shared.util.system import SystemInfo
# from shared.validation import ValidationResult, Validator, is_directory, is_in_range, is_timestamp

from .converters import default_converters
from .types import ConverterFn, ValidatorFn

# from shared.module_logger import LOGGER

APP_ROOT_DIR: Final[Path]        = Path(__file__).resolve().parent
CONFIG_PATH: Final[Path]         = APP_ROOT_DIR / "config"
DEFAULT_CONFIG_FILE: Final[Path] = CONFIG_PATH / "redecho.config"


# _TYPE_MAP: Final[Dict[type, str]] = {
#     bool:  'getboolean',
#     float: 'getfloat',
#     int:   'getint',
#     Path:  'get',
#     str:   'get',
# }




@dataclass
class BaseConfig:
	_field_map: ClassVar[Dict[str, Field]]

	_DEFAULT_SECTION: ClassVar[str] = "SETTINGS"

	_converter_registry: ClassVar[Dict[Type, ConverterFn]] = {}

	_validator_registry: Dict[str, List[ValidatorFn]] = field(default_factory=dict)

	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls._field_map = {f.name: f for f in fields(cls)}

		if "_converter_registry" not in cls.__dict__:
			cls._converter_registry = dict(cls._converter_registry)
		
		cls._converter_registry.update(default_converters)

	def __post_init__(self):
		self._validator_registry = {
			name: field.metadata.get("validators", [])
			for name, field in self._field_map.items()
		}

		self._config_errors: List[str] = []
		self._frozen: bool = False

	def __setattr__(self, name: str, value: Any) -> None:
		if getattr(self, "_frozen", False) and name in self._field_map:
			raise AttributeError( f"{self.__class__.__name__} is immutable after initialization")

		super().__setattr__(name, value)

	@classmethod
	def register_converter(cls, conv_type: type, fn: ConverterFn) -> None:
		# Ensure subclass get its own registry
		if "_converter_registry" not in cls.__dict__:
			cls._converter_registry = dict(cls._converter_registry)

		cls._converter_registry[conv_type] = fn

	def _convert(self, value: str, value_type: Type[Any]) -> Any:
		converter = self._converter_registry.get(value_type, None)
		if converter:
			return converter(self, value)

		return value_type(value)

	def _freeze(self) -> None:
		self._frozen = True

	def _validate(self, field_name: str, value: Any) -> Any:
		for func in self._validator_registry.get(field_name, ()):
			value = func(self, value)

		return value

	def load(self, path: Path) -> None:
		parser = configparser.ConfigParser(interpolation=None)

		parser.read(path)

		section = self._DEFAULT_SECTION

		if not parser.has_section(section):
			self._config_errors.append(f"Missing section: [{section}]")
			self._freeze()
			return

		data = parser[section]
		hints = get_type_hints(self.__class__)

		for f in fields(self):
			# Skip private and protected variables
			if f.name.startswith('_'):
				continue

			# Skip fields that are not in the config file
			if f.name not in data:
				continue

			raw_value = data[f.name]

			try:
				value = self._convert(raw_value, hints[f.name])
				value = self._validate(f.name, value)
				super().__setattr__(f.name, value)
			except Exception as e:
				self._config_errors.append(f"{f.name}: {e}")

			self._freeze()
