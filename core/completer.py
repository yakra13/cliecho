"""
"""
import readline
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
# from typing import Dict, List, Optional

# from core.command_registry import CommandNode, build_command_registry
from core.dispatcher import Dispatcher
# from core.module_loader import ModuleLoader
from core.command_registry import CommandNode, build_command_registry

# from core.dispatcher import Dispatcher

# @dataclass
# class CommandNode:
#     """Dataclass representing a command line token."""
#     completer: Optional[Callable[[List[str]], List[str]]] = None
#     handler: Optional[str] = None
#     children: Dict[str, "CommandNode"] = field(default_factory=dict)
#     module_only: bool = False
#     flags: List[str] = field(default_factory=list)


# pylint: disable=too-few-public-methods
class Completer:
    """Handles command tab completion and cli setup."""
    _matches: list[str] = []

    @classmethod
    def setup(cls):
        """Prepares the command line for tab completions."""
        readline.set_completer(cls._completer)
        readline.parse_and_bind('tab: complete')

    @classmethod
    def _compute_matches(cls, text: str) -> List[str]:
        line: str = readline.get_line_buffer()
        parts: List[str] = line.lstrip().split()

        registry: Dict[str, CommandNode] = build_command_registry()

        if len(parts) == 0 or (len(parts) == 1 and not line.endswith(" ")):
            return [
                c for c, node in registry.items()
                if not node.module_only
                and not Dispatcher().current_module
                and c.lower().startswith(text.lower())
            ]

        cmd = parts[0]
        args = parts[1:]

        node = registry.get(cmd)
        if not node:
            return []

        completions = cls._node_completions(node=node, args=args)

        return [c for c in completions if c.startswith(text.lower())]

    @staticmethod
    def _node_completions(node: CommandNode, args: List[str]) -> List[str]:
        if node.children:
            last_arg = args[-1] if args else ""

            return [
                name for name, n in node.children.items()
                if not n.module_only
                and not Dispatcher().current_module
                and name.startswith(last_arg.lower())
            ]

        if node.completer:
            return node.completer(args)

        return []

    @classmethod
    def _completer(cls, text: str, state: int) -> Optional[str]:
        # Compute matches only on state 0 (first word of the command)
        if state == 0:
                cls._matches = cls._compute_matches(text)

        try:
            return cls._matches[state]
        except IndexError:
            return None


# def build_command_registry() -> Dict[str, CommandNode]:
#     """Builds the command tree and returns a copy."""
#     return {
#         'show': CommandNode(children={
#             'modules': CommandNode(handler='handle_show_modules'),
#             'options': CommandNode(handler='handle_show_options', module_only=True),
#             'presets': CommandNode(handler='handle_show_presets', module_only=True)
#             }),
#         'info':   CommandNode(completer=lambda _: ModuleLoader().get_modules_list(),
#                               handler='handle_info'),
#         'use':    CommandNode(completer=lambda _: ModuleLoader().get_modules_list(),
#                               handler='handle_use'),
#         'set':    CommandNode(completer=lambda _: Dispatcher().get_module_params(),
#                               handler='handle_set', module_only=True),
#         'preset': CommandNode(module_only=True, children={
#             'save': CommandNode(handler='handle_preset_save', module_only=True),
#             'load': CommandNode(handler='handle_preset_load', module_only=True),
#             }),
#         'exit': CommandNode(handler='handle_exit'),
#         'help': CommandNode(handler='handle_help'),
#     }
