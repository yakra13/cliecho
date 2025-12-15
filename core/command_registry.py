from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from core.dispatcher import Dispatcher
from core.module_loader import ModuleLoader

@dataclass
class CommandNode:
    """
    Docstring for CommandNode
    """
    completer: Optional[Callable[[List[str]], List[str]]] = None
    handler: Optional[str] = None
    children: Dict[str, "CommandNode"] = field(default_factory=dict)
    module_only: bool = False

class CommandRegistry:
    """
    Docstring for CommandRegistry
    """
    @classmethod
    def build(cls) -> Dict[str, CommandNode]:
        return {
            'show': CommandNode(children={
                'modules': CommandNode(handler='handle_show_modules'),
                'options': CommandNode(handler='handle_show_options', module_only=True),
                'presets': CommandNode(handler='handle_show_presets', module_only=True)
                }),
            'info':   CommandNode(completer=lambda _: ModuleLoader().get_modules_list(), handler='handle_info'),
            'use':    CommandNode(completer=lambda _: ModuleLoader().get_modules_list(), handler='handle_use'),
            'set':    CommandNode(completer=lambda _: Dispatcher().get_module_params(), handler='handle_set', module_only=True),
            'preset': CommandNode(module_only=True, children={
                'save': CommandNode(handler='handle_preset_save', module_only=True),
                'load': CommandNode(handler='handle_preset_load', module_only=True),
                }),
            'exit': CommandNode(handler='handle_exit'),
            'help': CommandNode(handler='handle_help'),
        }
