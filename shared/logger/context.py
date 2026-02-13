from dataclasses import asdict, dataclass, is_dataclass
from typing import Dict, Mapping


@dataclass
class Context:
	name: str
	destination: str


def normalize_context(context: Context) -> Dict:
    if context is None:
        return {}
    
    if is_dataclass(context):
        return asdict(context)

    if isinstance(context, Mapping):
        return dict(context)

    # Fallback
    return vars(context)