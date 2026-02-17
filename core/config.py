import configparser
from dataclasses import dataclass, field, fields
# from datetime import datetime
from pathlib import Path
from typing import Any, Final, List, Literal, Optional

# from shared.validation import validate_thread_count, timestamp_format
from shared.module_logger import EventLevel
from shared.task import TaskMessage, TaskResult
from shared.util.util import SystemInfo
from shared.validation import ValidationResult, Validator, is_directory, is_in_range, is_timestamp

# from shared.module_logger import LOGGER

APP_ROOT_DIR: Final[Path]        = Path(__file__).resolve().parent
CONFIG_PATH: Final[Path]         = APP_ROOT_DIR / "config"
DEFAULT_CONFIG_FILE: Final[Path] = CONFIG_PATH / "redecho.config"

@dataclass
class AppConfig():
    """
    Docstring for AppConfig
    """
    _DEFAULT_SECTION: Final[str] = "SETTINGS"

    _config_errors: List[TaskMessage] = field(default_factory=list, repr=False)
    _initialized: bool = field(default=False, repr=False)

    # Directories
    # TODO: validator for Path vars?
    modules_path: Path    = field(
        default=APP_ROOT_DIR / "modules",
        metadata={'validator': is_directory,
                  'auto_create': True})

    presets_path: Path    = field(
        default=APP_ROOT_DIR / "presets",
        metadata={'validator': is_directory,
                  'auto_create': True})

    logs_path: Path       = field(
        default=APP_ROOT_DIR / "logs",
        metadata={'validator': is_directory,
                  'auto_create': True})

    output_path: Path     = field(
        default=APP_ROOT_DIR / "output",
        metadata={'validator': is_directory,
                  'auto_create': True})

    extracted_path: Path  = field(
        default=APP_ROOT_DIR / ".extracted",
        metadata={'validator': is_directory,
                  'auto_create': True})

    guardrails_path: Path = field(
        default=APP_ROOT_DIR / "guardrails",
        metadata={'validator': is_directory,
                  'auto_create': True})

    verbosity: int = field(
        default=1,
        metadata={'validator': is_in_range(1, 2)})

    timestamp_format: str = field(
        default="%Y-%m-%d %H:%M:%S",
        metadata={'validator': is_timestamp})

    enable_ansi: bool       = True

    enable_guardrails: bool = True

    enable_threading: bool  = True

    enable_duplicate_module_threads: bool = False # Run multiple threads of the same module

    max_thread_count: int   = field(
        default=0,
        metadata={'validator': is_in_range(0, SystemInfo.get_system_max_threads()),
        'error': f"Valid range 0 - {SystemInfo.get_system_max_threads()}"}) # 0 = automatic

    # def __init__(self):
    # @property
    # def errors(self) -> List[str]:
    #     return self._config_errors

    # def __post_init__(self):
    #     LOGGER.console_raw("Loading RedEcho configuration from file...")
    #     self.load_default_settings()
    #     # Display any errors found when loading config file
    #     err_count = len(self._config_errors)

    #     if err_count == 0:
    #         LOGGER.console_raw("Successfully loaded configuration from file.")
    #     else:
    #         LOGGER.console_raw(f"{err_count} error{'s' if err_count > 1 else ''} found:")
    #         for err in self._config_errors:
    #             LOGGER.console_error(err)
    #     self._initialized = True

    def __setattr__(self, name: str, value: Any) -> None:
        # Override changing attributes after initalization
        if getattr(self, "_initialized", False) and not name.startswith('_'):
            # Configuration values are read only after loading
            raise AttributeError(f"AppConfig field '{name}' is read-only after loading.")
        super().__setattr__(name, value)

    def build_workspace_task(self) -> TaskResult:
        # messages: List[str] = []
        task_result: TaskResult = TaskResult(False, [])

        if not self._initialized:
            return TaskResult(
                True,
                [TaskMessage(EventLevel.ERROR, "Configuration must be loaded first")])

        # print(self.modules_path)
        # print(self.presets_path)
        # print(self.logs_path)
        # print(self.output_path)
        # print(self.extracted_path)
        # print(self.guardrails_path)

        for f in fields(self):
            path = getattr(self, f.name)

            if isinstance(path, Path) and f.metadata.get('auto_create', False):
                already_exists = path.is_dir()
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    if not already_exists:
                        # messages.append(f"Created missing directory: {path.name}")
                        task_result.messages.append(
                        TaskMessage(EventLevel.INFO, f"Created missing directory: {path.name}"))
                except (PermissionError, OSError) as e:
                    # messages.append(f"Could not create {path}: {e}")
                    task_result.messages.append(
                        TaskMessage(EventLevel.WARN, f"Could not create {path}: {e}"))

        return task_result

    def load_config_task(self, config_path: Path = DEFAULT_CONFIG_FILE) -> TaskResult:
        # Prevent reloading config settings
        # TODO: may want to allow some settings to be changed during run

        if self._initialized:
            return TaskResult(True, [TaskMessage(EventLevel.INFO, "Already initialized")])

        type_mapping = {
            int: 'getint',
            bool: 'getboolean',
            float: 'getfloat',
            str: 'get',
            Path: 'get'
        }

        parser = configparser.ConfigParser(interpolation=None)

        parser.read(config_path)

        if self._DEFAULT_SECTION not in parser:
            self._config_errors.append(TaskMessage(EventLevel.ERROR,
                f"Required '[{self._DEFAULT_SECTION}]' section label not found."))
            return TaskResult(False, self._config_errors)

        for f in fields(self):
            # Skip private and protected variables
            if f.name.startswith('_'):
                continue

            # Skip fields that are not in the config file
            if not f.name in parser[self._DEFAULT_SECTION]:
                continue

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

                self._config_errors.append(TaskMessage(EventLevel.WARN,
                    f"Invalid {t} for '{f.name}': '{r}' using default: {f.default}"))

            except (OSError, RuntimeError) as e:
                r = parser.get(self._DEFAULT_SECTION, f.name)

                self._config_errors.append(TaskMessage(EventLevel.WARN,
                    f"Path '{r}' is invalid: {e} using default: {f.default}"))

            else:
                # Perform validation
                validator: Optional[Validator] = f.metadata.get('validator')

                error: Optional[str] = None

                if value is None:
                    # Should be caught in the ValueError except
                    error = f"{f.metadata.get('error', '')}"
                elif validator:
                    result: ValidationResult = validator(value)

                    if result.error:
                        error = result.error
                    elif not result.is_valid:
                        error = f"{f.metadata.get('error', '')}"

                if error:
                    self._config_errors.append(TaskMessage(EventLevel.WARN,
                        f"Invalid value '{f.name}': {value}; {error}; using default: {f.default}"))
                else:
                    # Set the value
                    setattr(self, f.name, value)

        # Denote that default settings have been loaded
        self._initialized = True
        if err_count := len(self._config_errors) > 0:
            err_task_msg = TaskMessage(EventLevel.ERROR, 
                f"{err_count} error{'s' if err_count > 1 else ''} detected in configuration.")
            self._config_errors.insert(0, err_task_msg)

        return TaskResult(True, self._config_errors)

CONFIG = AppConfig()
# CONFIG.load_default_settings()

# TODO: Check if there are errors and output them
