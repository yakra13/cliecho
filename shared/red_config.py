"""
TODO:
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final

from shared.app_config.config import BaseConfig
from shared.logger.formatter import Verbosity # TODO: move verbosity somewhere else
from shared.app_config.converters import enum_converter
from shared.app_config.field_validators import clamp, in_range, is_directory, is_timestamp
from shared.util.system import SystemInfo

APP_ROOT_DIR: Final[Path]        = Path(__file__).resolve().parent
CONFIG_PATH: Final[Path]         = APP_ROOT_DIR / "config"
DEFAULT_CONFIG_FILE: Final[Path] = CONFIG_PATH / "redecho.config"

@dataclass
class RedEchoConfig(BaseConfig): # pylint: disable=too-many-instance-attributes
	"""Global configuration values."""
	modules_path: Path = field(default=APP_ROOT_DIR / "modules",
							   metadata={'validator': [is_directory]})
	presets_path: Path = APP_ROOT_DIR / "presets"
	logs_path: Path = APP_ROOT_DIR / "logs"

	output_path: Path = APP_ROOT_DIR / "output"

	extracted_path: Path = APP_ROOT_DIR / ".extracted"

	guardrails_path: Path = APP_ROOT_DIR / "guardrails"

	verbosity: Verbosity = field(default=Verbosity.NORMAL,
								 metadata={'validator': [clamp(Verbosity.MINIMAL, Verbosity.DEBUG)]})

	timestamp_format: str = field(default="%Y-%m-%d %H:%M:%S",
								  metadata={'validator': [is_timestamp]})

	enable_ansi: bool       = True

	enable_guardrails: bool = True

	enable_threading: bool  = True
	# Run multiple threads of the same module
	enable_duplicate_module_threads: bool = False 

 	# 0 = automatic
	max_thread_count: int = field(default=0,
								  metadata={'validator': [in_range(0, SystemInfo.get_system_max_threads())]})

# Register converters required for any non-default types
RedEchoConfig.register_converter(Verbosity, enum_converter(Verbosity))
