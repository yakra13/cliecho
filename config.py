import configparser
from dataclasses import dataclass, field, fields
from datetime import datetime
from pathlib import Path
from typing import Any, Final, List, Literal

# from shared.validation import validate_thread_count, timestamp_format
import shared.validation as Validate
from shared.module_logger import LOGGER

APP_ROOT_DIR: Final[Path]        = Path(__file__).resolve()
CONFIG_PATH: Final[Path]         = APP_ROOT_DIR / "config"
DEFAULT_CONFIG_FILE: Final[Path] = CONFIG_PATH / "redecho.config"

@dataclass
class AppConfig():
    """
    Docstring for AppConfig
    """
    _config_errors: List[str] = field(default_factory=list, repr=False)
    _DEFAULT_SECTION: Final[str] = "SETTINGS"
    _initialized: bool = field(default=False, repr=False)

    # Directories
    # TODO: validator for Path vars?
    modules_path: Path    = APP_ROOT_DIR / "modules"
    presets_path: Path    = APP_ROOT_DIR / "presets"
    logs_path: Path       = APP_ROOT_DIR / "logs"
    output_path: Path     = APP_ROOT_DIR / "output"
    extracted_path: Path  = APP_ROOT_DIR / ".extracted"
    guardrails_path: Path = APP_ROOT_DIR / "guardrails"

    verbosity: int = field(
        default=1,
        metadata={'validator': lambda x: 1 <= x <= 2})
    timestamp_format: str = field(
        default="%Y-%m-%d %H:%M:%S",
        metadata={'validator': Validate.timestamp_format})

    enable_ansi: bool       = True
    enable_guardrails: bool = True
    enable_threading: bool  = True
    max_thread_count: int   = field(
        default=0,
        metadata={'validator': Validate.thread_count}) # 0 = automatic
    enable_duplicate_module_threads: bool = False # Run multiple threads of the same module

    def __init__(self):
        LOGGER.console_raw("Loading RedEcho configuration from file...")
        self._load_from_file()
        # Display any errors found when loading config file
        err_count = len(self._config_errors)

        if err_count == 0:
            LOGGER.console_raw("Successfully loaded configuration from file.")
        else:
            LOGGER.console_raw(f"{err_count} error{'s' if err_count > 1 else ''} found:")
            for err in self._config_errors:
                LOGGER.console_error(err)

    def __post_init__(self):
        self._initialized = True

    def __setattr__(self, name: str, value: Any) -> None:
        # Override changing attributes after initalization
        if getattr(self, "_initialized", False) and not name.startswith('_'):
            # Configuration values are read only after loading
            raise AttributeError(f"AppConfig field '{name}' is read-only after loading.")
        super().__setattr__(name, value)

    def _load_from_file(self):
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
                # Determine the getter function based of var type, default to string
                getter_name = type_mapping.get(f.type, "get")
                getter = getattr(parser, getter_name)

                try:
                    # Get the value with the appropriate getter
                    # Throws ValueError if type doesn't match getter
                    value = getter(self._DEFAULT_SECTION, f.name)

                    # Handle special conversions
                    match f.type:
                        case type_ if type_ is Path:
                            # Handle relative and absolute paths
                            # Possible exceptions OSError/RuntimeError
                            value = (APP_ROOT_DIR / value).resolve()

                except ValueError:
                    # Type validation
                    r = parser.get(self._DEFAULT_SECTION, f.name)
                    t = str(f.type).split('.')[-1].replace("'>", "")

                    self._config_errors.append(
                        f"Invalid {t} for '{f.name}': '{r}' using default: {f.default}")

                except (OSError, RuntimeError) as e:
                    r = parser.get(self._DEFAULT_SECTION, f.name)

                    self._config_errors.append(
                        f"Path '{r}' is invalid: {e} using default: {f.default}")

                else:
                    # Perform validation
                    validator = f.metadata.get('validator')

                    if not value or validator and not validator(value):
                        self._config_errors.append(
                            f"Invalid value '{f.name}': {value} using default: {f.default}")
                        continue # Keep default setting

                    # Set the value
                    setattr(self, f.name, value)

CONFIG = AppConfig()
CONFIG._load_from_file()

# TODO: Check if there are errors and output them
