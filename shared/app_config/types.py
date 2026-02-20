from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
	from .config import BaseConfig


ConverterFn = Callable[[BaseConfig, str], Any]
ValidatorFn = Callable[[BaseConfig, Any], Any]