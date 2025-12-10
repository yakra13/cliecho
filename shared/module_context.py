from dataclasses import dataclass, field
from typing import Any, Dict

@dataclass
class ModuleContext:
    name: str
    options: Dict[str, Any] = field(default_factory=Dict)