from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Mapping
from uuid import uuid4

from util.sanitize import sanitize_filename

@dataclass
class Context:
	name: str
	sanitized_name: str = field(init=False, repr=False)
	id: str = field(init=False, repr=False)
	# destination: str
	# TODO: standardize/globalize timezone
	timestamp: int = field(init=False, repr=False)

	def __post_init__(self):
        # sanitize the provided name for use in file names
		self.sanitized_name = sanitize_filename(self.name)
		# Generate a unique identifier from uuid, timestamp, and name
		ts = int(datetime.now(timezone.utc).timestamp())
		self.timestamp = ts

		self.id = f"{ts}_{uuid4().hex}_{self.sanitized_name}"

@dataclass
class ModuleContext(Context):
    module_options: Dict[str, Any] = field(default_factory=Dict)


def normalize_context(context: Context) -> Dict:
    if context is None:
        return {}
    
    if is_dataclass(context):
        return asdict(context)

    if isinstance(context, Mapping):
        return dict(context)

    # Fallback
    return vars(context)