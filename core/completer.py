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
# from core.output_formatter import format_list_as_grid
from shared.ansi import AnsiStyle
from shared.color import Color
from shared.formatter import format_list_as_grid, style_text

# Type definition for command line completer function
CompleterFn = Callable[[str, int], Optional[str]]

# pylint: disable=too-few-public-methods
class Completer:
    """Handles command tab completion and cli setup."""
    _matches: list[str] = []
    _flag_help: Optional[str] = None
    _original_completer: Optional[CompleterFn] = None

    @classmethod
    def setup(cls) -> None:
        """Prepares the command line for tab completions."""
        cls._original_completer = readline.get_completer()
        readline.set_completer(cls._completer)
        readline.parse_and_bind('tab: complete')
        readline.set_completion_display_matches_hook(cls._display_matches_hook)

    @classmethod
    def teardown(cls):
        """
        Returns the completer to the original completer.
        Should be preformed before exiting.
        """
        if cls._original_completer is not None:
            readline.set_completer(cls._original_completer)

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

            return valid_tokens

        cmd = parts[0]
        args = parts[1:]

        node = registry.get(cmd)
        # If the command doesnt exist or requires a current module return empty list
        # Prevents showing completions for commands that arent valid in the current state
        if not node or node.module_only and not Dispatcher().current_module:
            return []

        completions = cls._node_completions(node=node, args=args)

        # Return possible completions that match the current user input
        if completions:
            return [c for c in completions if c.startswith(text.lower())]
        
        # If the command node has flags gather those for display
        if node.flags:
            cls._flag_help = ''
            for flag in node.flags:
                cls._flag_help += f"    {flag.short} [{flag.full}]\t{flag.description}\n"

        return []

    @staticmethod
    def _node_completions(node: CommandNode, args: List[str]) -> List[str]:
        """Return possible completions for the current command node."""
        if node.children:
            last_arg = args[-1] if args else ""
            # Gets a list of all children that are valid options for the current state
            # ie if a command requires a current module and there is none then do not show it
            return [
                name for name, n in node.children.items()
                if not n.module_only
                and not Dispatcher().current_module
                and name.startswith(last_arg.lower())
            ]

        # Perform custom completions; ie finding the available modules in a command like 'use {module}'
        if node.completer:
            return node.completer(args)

        return []

    @classmethod
    def _completer(cls, text: str, state: int) -> Optional[str]:
        # Compute matches only on state 0 (first word of the command)
        if state == 0:
            cls._matches = cls._compute_matches(text)

            # If a command contains flag parameters handle showing them
            if cls._flag_help:
                cls._display_matches_hook(None, None, None)
                readline.redisplay()

        try:
            return cls._matches[state]
        except IndexError:
            return None

    @classmethod
    def _display_matches_hook(cls, substitution, matches, longest_match_length):
        """Handles custom display formatting of completions"""
        # TODO: custom formatter for auto complete suggestions
        sys.stdout.write('\n')

        # NOTE: Test code to check coloring/formatting
        # for i in range(0, len(matches)):
        #     if i % 2 == 0:
        #         matches[i] = style_text(text=matches[i],
        #                                 text_color=Color.Cyan,
        #                                 back_color=Color.DarkGray,
        #                                 styles=[AnsiStyle.BOLD])

        if cls._flag_help:
            # Display help info for command flags
            sys.stdout.write(cls._flag_help)
            cls._flag_help = None
        elif len(matches) > 4:
            # Display completions as a grid
            sys.stdout.write(format_list_as_grid(matches, columns=4, auto_size=True))
        else:
            # Display completions in a single column
            sys.stdout.write(format_list_as_grid(matches)) # default 1 column
            
        # Redraw prompt and input     
        # NOTE: Returns cursor to beginning of line and erases from current cursor position to the end of the line   
        # sys.stdout.write("\r\033[K")
        sys.stdout.write('\n')
        sys.stdout.write(CLIManager().get_prompt() + readline.get_line_buffer())
        sys.stdout.flush()
