"""
"""
import readline
from dataclasses import dataclass, field
import sys
from typing import Callable, Dict, List, Optional
# from typing import Dict, List, Optional

# from core.command_registry import CommandNode, build_command_registry
from core.cli_manager import CLIManager
from core.dispatcher import Dispatcher
# from core.module_loader import ModuleLoader
from core.command_registry import CommandNode, build_command_registry
from core.output_formatter import format_list_as_table

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
    _flag_help: Optional[str] = None

    @classmethod
    def setup(cls):
        """Prepares the command line for tab completions."""

        readline.set_completer(cls._completer)
        readline.parse_and_bind('tab: complete')
        readline.set_completion_display_matches_hook(cls._display_matches_hook)

    @classmethod
    def _compute_matches(cls, text: str) -> List[str]:
        line: str = readline.get_line_buffer()
        parts: List[str] = line.lstrip().split()

        registry: Dict[str, CommandNode] = build_command_registry()

        if len(parts) == 0 or (len(parts) == 1 and not line.endswith(" ")):
            valid_tokens: List[str] = []
            for token, node in registry.items():
                # If the node requires a module in use but there isnt one then skip
                if node.module_only and not Dispatcher().current_module:
                    continue

                if token.lower().startswith(text.lower()):
                    valid_tokens.append(token)

            # valid_tokens = [
            #     c for c, node in registry.items()
            #     if not node.module_only and not Dispatcher().current_module
            #     and c.lower().startswith(text.lower())
            # ]
            return valid_tokens

        cmd = parts[0]
        args = parts[1:]

        node = registry.get(cmd)
        if not node:
            return []

        completions = cls._node_completions(node=node, args=args)

        if completions:
            return [c for c in completions if c.startswith(text.lower())]
        
        if node.flags:
            cls._flag_help = ''
            for flag in node.flags:
                cls._flag_help += f"    {flag.short} [{flag.full}]\t{flag.description}\n"

        return []

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

            if cls._flag_help:
                cls._display_matches_hook(None, None, None)
                readline.redisplay()

        try:
            return cls._matches[state]
        except IndexError:
            return None
    @classmethod
    def _display_matches_hook(cls, substitution, matches, longest_match_length):
        # TODO: custom formatter for auto complete suggestions
        sys.stdout.write('\n')

        for i in range(0, len(matches)):
            if i % 2 == 0:
                matches[i] = f"\033[1;36;40m{matches[i]}\033[0m "
            else:
                matches[i] = f"\033[37m{matches[i]}\033[0m "

        if cls._flag_help:
            # Display help info for command flags
            sys.stdout.write(cls._flag_help)
            cls._flag_help = None
        elif len(matches) > 4:
            # Display as table
            sys.stdout.write(format_list_as_table(matches, columns=4))
        else:
            # Display in single column
            sys.stdout.write(format_list_as_table(matches)) # default 1 column
            
        # Redraw prompt and input        
        # sys.stdout.write("\r\033[K")
        sys.stdout.write('\n')
        sys.stdout.write(CLIManager().get_prompt() + readline.get_line_buffer())

        sys.stdout.flush()


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
