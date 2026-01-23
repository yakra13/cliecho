import configparser
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Final, List, Literal

APP_ROOT_DIR: Path = Path(__file__).resolve()
CONFIG_PATH: Path = APP_ROOT_DIR / "config"
DEFAULT_CONFIG_FILE: Path = CONFIG_PATH / "redecho.config"

@dataclass
class AppConfig():
    """
    Docstring for AppConfig
    """
    CONFIG_VALUE_1: str = "default value"
    CONFIG_VALUE_2: str = "default value"
    CONFIG_VALUE_3: int = 0
    CONFIG_VALUE_4: bool = False

    # Directories
    modules_path: Path    = APP_ROOT_DIR / "modules"
    presets_path: Path    = APP_ROOT_DIR / "presets"
    logs_path: Path       = APP_ROOT_DIR / "logs"
    output_path: Path     = APP_ROOT_DIR / "output"
    extracted_path: Path  = APP_ROOT_DIR / ".extracted"
    guardrails_path: Path = APP_ROOT_DIR / "guardrails"

    verbosity: int = 3
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"

    enable_ansi: bool      = True
    enable_guardrails: bool = True
    enable_threading: bool = True
    max_thread_count: int  = 0 # 0 = automatic
    enable_duplicate_module_threads: bool = False # Run multiple threads of the same module

    _config_errors: List[str] = field(default_factory=list, repr=False)
    _DEFAULT_SECTION: Final[str] = "SETTINGS"

    def load_from_file(self):
        type_mapping = {
            int: 'getint',
            bool: 'getboolean',
            float: 'getfloat',
            str: 'get',
            Path: 'get'
        }

        parser = configparser.ConfigParser()

        parser.read(DEFAULT_CONFIG_FILE)

        if self._DEFAULT_SECTION not in parser:
            self._config_errors.append(
                f"Required '[{self._DEFAULT_SECTION}]' section label not found.")
            return

        for f in fields(self):
            # Skip private and protected variables
            if f.name.startswith('_'):
                continue
            
            if f.name in parser[self._DEFAULT_SECTION]:
                # Determine the getter function based of var type
                getter_name = type_mapping.get(f.type, "get")
                getter = getattr(parser, getter_name)

                try:
                    # Get the value with the appropriate getter
                    value: Any = getter(self._DEFAULT_SECTION, f.name)

                    # Handle special conversions
                    match f.type:
                        case type_ if type_ is Path:
                            # Handle relative and absolute paths
                            value = (APP_ROOT_DIR / value).resolve()

                    # Set the value
                    setattr(self, f.name, value)

                except ValueError:
                    raw_str = parser.get(self._DEFAULT_SECTION, f.name)
                    type_name = str(f.type).split('.')[-1].replace("'>", "")
                    self._config_errors.append(f"Invalid {type_name} for '{f.name}': '{raw_str}'")
                except (OSError, RuntimeError) as e:
                    raw_str = parser.get(self._DEFAULT_SECTION, f.name)
                    self._config_errors.append(f"Path '{raw_str}' is invalid: {e}")


CONFIG = AppConfig()
CONFIG.load_from_file()

# Check if there are errors and output them
