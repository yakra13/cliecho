from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class ModuleContext:
    """Store the module context used in logging."""
    name: str
    options: Dict[str, Any] = field(default_factory=Dict)