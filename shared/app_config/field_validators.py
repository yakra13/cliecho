"""
TODO:
"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from .types import ValidatorFn, Number

if TYPE_CHECKING:
	from .config import BaseConfig

####################
# Helper Functions #
####################

def _check_bounds(min_value: Number, max_value: Number) -> None:
	if min_value > max_value:
		raise ValueError("min_value cannot be greater than max_value")


##############################
# Field Validation Functions #
##############################

def clamp(min_value: Number, max_value: Number) -> ValidatorFn:
	"""
	Clamps a Number between min and max value.

	Will cast the result to the type of the value.
	Allowing IntEnums to be clamped as well as numbers.
	"""
	_check_bounds(min_value, max_value)

	def validate(_: BaseConfig, value: Number) -> Number:
		result: Number = max(min_value, min(max_value, value))
		# Preserve original type
		return type(value)(result)

	return validate

def in_range(min_value: Number, max_value: Number) -> ValidatorFn:
	"""Validates a Number falls within the specified range."""
	_check_bounds(min_value, max_value)

	def validate(_: BaseConfig, value: Number) -> Number:
		if min_value > value > max_value:
			raise ValueError(F"{value} is not within the range {min_value} - {max_value}")
		return value

	return validate

def non_empty() -> ValidatorFn:
	"""TODO"""
	def validate(_: BaseConfig, value: str) -> str:
		if not value.strip():
			raise ValueError("String cannot be empty")
		return value

	return validate

def must_exist() -> ValidatorFn:
	"""TODO"""
	def validate(_: BaseConfig, value: Path) -> Path:
		if not value.exists():
			raise ValueError(f"{value} does not exist")
		return value

	return validate

def is_directory() -> ValidatorFn:
	"""TODO"""
	def validate(_: BaseConfig, value: Path) -> bool:
		if value.is_file():
			raise NotADirectoryError(f"{value} is not a directory")
		return value

	return validate

def is_timestamp() -> ValidatorFn:
	"""Validates a given string is valid timestamp format."""
	def validate(_: BaseConfig, value: str) -> str:
		try:
			datetime.now().strftime(value)
		except (ValueError, TypeError) as e:
			raise ValueError(f"{value} is invalid format") from e
		return value

	return validate
