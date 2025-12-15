"""
"""
import readline
from typing import Dict, List, Optional

from core.command_registry import CommandNode, CommandRegistry
from core.dispatcher import Dispatcher

# pylint: disable=too-few-public-methods
class Completer:
    """
    Docstring for Completer
    """
    _matches: list[str] = []

    @classmethod
    def setup(cls):
        """
        Docstring for setup
        """
        readline.set_completer(cls._completer)
        readline.parse_and_bind('tab: complete')

    @classmethod
    def _compute_matches(cls, text: str) -> List[str]:
        line: str = readline.get_line_buffer()
        parts: List[str] = line.lstrip().split()

        registry: Dict[str, CommandNode] = CommandRegistry().build()

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
        """
        Docstring for completer
        """
        if state == 0:
            cls._matches = cls._compute_matches(text)
        
        try:
            return cls._matches[state]
        except IndexError:
            return None
