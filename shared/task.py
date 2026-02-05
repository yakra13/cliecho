

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from shared.color import Color
from shared.formatter import style_text
from shared.log_types import EventLevel
from shared.module_logger import LOGGER


def _default_logging_callback(task_result: "TaskResult"):
    if not task_result:
        return
    
    for msg in task_result.messages:
        color = msg.event_level.color
        LOGGER.console_raw(style_text(msg.message, color))

@dataclass
class TaskMessage():
    event_level: EventLevel
    message: str

@dataclass
class TaskResult():
    success: bool
    messages: List[TaskMessage]

@dataclass
class Task():
    name: str
    action: Callable[[], TaskResult]
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)

    callback: Callable[[TaskResult], None] = _default_logging_callback

    # result: Optional[TaskResult] = None
    errors: Optional[str] = None

    def execute(self) -> bool:
        try:
            result = self.action(*self.args, **self.kwargs)
        except Exception as e:
            self.errors = str(e)
            return False
        
        # if self.callback:
        self.callback(result)
        # else:
        #     # No specific callback defined so just color based on event level
        #     for message in result.messages:
        #         styled = style_text(message.message, message.event_level.color)
        #         LOGGER.console_raw(styled)

        return result.success

