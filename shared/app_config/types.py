"""
TODO this area
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, TypeAlias

if TYPE_CHECKING:
	from .config import BaseConfig


ConverterFn: TypeAlias = Callable[[BaseConfig, str], Any]
ValidatorFn: TypeAlias = Callable[[BaseConfig, Any], Any]

Number: TypeAlias = int | float
