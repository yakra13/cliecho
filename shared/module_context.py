from dataclasses import dataclass, field
from typing import Any

@dataclass
class ModuleContext:
    name: str
    options: dict[str, Any] = field(default_factory=dict)