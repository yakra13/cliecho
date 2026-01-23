
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from core.util.singleton import Singleton

RED_ECHO_ROOT: Path

@dataclass
class Configuration(Singleton):
    """Global configuration settings."""
    _modules_path: Path
    _presets_path: Path
    _log_path: Path
    _output_path: Path
    _extracted_modules_path: Path
    _verbosity: int

    _console_timestamp_format: Callable
    _log_timestamp_format: Callable
    _job_id_format: Callable


    _config_path: Path = Path("config")
    _config_file: Path = _config_path / "redecho.config"
    _guardrail_file: Path = _config_file / "redecho.guard"

    _support_ansi_encoding: bool = True
    _support_job_threads: bool   = True
    _support_duplicate_module_threads: bool = False

    _require_guardrails: bool = False