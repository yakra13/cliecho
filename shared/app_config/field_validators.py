from .types import ValidatorFn


def clamp(min_value: int, max_value: int) -> ValidatorFn:
	def validate(_, value: int) -> int:
		return max(min_value, min(max_value, value))
	return validate

def non_empty() -> ValidatorFn:
	def validate(_, value: str) -> str:
		if not value.strip():
			raise ValueError("String cannot be empty")
		return value
	return validate

def must_exist() -> ValidatorFn:
	from pathlib import Path
	def validate(_, value: Path) -> Path:
		if not value.exists():
			raise ValueError(f"{value} does not exist")
		return value
	return validate