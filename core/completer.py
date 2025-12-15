"""
"""
import readline
from typing import List, Optional

from core.dispatcher import Dispatcher
from core.module_loader import ModuleLoader

# pylint: disable=too-few-public-methods
class Completer:
    """
    Docstring for Completer
    """
    @classmethod
    def setup(cls):
        """
        Docstring for setup
        
        :param cls: Description
        """
        readline.set_completer(cls._completer)
        readline.parse_and_bind('tab: complete')

    @classmethod
    def _completer(cls, text: str, state: int) -> Optional[str]:
        """
        Docstring for completer
        
        :param cls: Description
        :param text: Description
        :type text: str
        :param state: Description
        :type state: int
        :return: Description
        :rtype: str | None
        """
        line: str          = readline.get_line_buffer()
        parts: List[str]   = line.lstrip().split()
        options: List[str] = []

        if len(parts) == 0 or (len(parts) == 1 and not line.endswith(" ")):
            for cmd, _ in cls.COMMANDS.items():
                # Show only commands valid for the current state
                if cmd in ['exit', 'use', 'show', 'info'] or \
                    (cmd in ['set', 'preset'] and cls._module_in_use()):
                    if cmd.lower().startswith(text.lower()):
                        options.append(cmd)
        else:
            parent_cmd = parts[0]
            args_so_far = parts[1:]
            if parent_cmd in cls.COMMANDS:
                completions = cls.COMMANDS[parent_cmd](args_so_far)
                if line.endswith(" "):
                    options = completions
                else:
                    options = [c for c in completions if c.lower().startswith(text.lower())]

        try:
            return options[state]
        except IndexError:
            return None

    @classmethod
    def _module_in_use(cls) -> bool:
        """
        Docstring for module_in_use
        
        :param cls: Description
        :return: Description
        :rtype: bool
        """
        return Dispatcher().current_module is not None

    @classmethod
    def _get_module_names(cls) -> List[str]:
        m = ModuleLoader()
        return m.get_modules_list()

    @classmethod
    def _get_module_params(cls) -> List[str]:
        d = Dispatcher()
        return d.get_current_module_params()

    @classmethod
    def _build_commands(cls):
        return {
            'show': lambda args:
                ['modules', 'options', 'presets'] if cls._module_in_use() else ['modules'],
            'info': lambda args:
                cls._get_module_names() if not cls._module_in_use() else [],
            'use': lambda args:
                cls._get_module_names(),
            'set': lambda args:
                cls._get_module_params() if cls._module_in_use() else [],
            'preset': lambda args:
                ['save', 'load'] if cls._module_in_use() else [],
            'exit': lambda args: [],
            'help': lambda args: [],
        }

    # Called at class creation
    COMMANDS = _build_commands.__func__()

# TODO: complete logic for new CommandNodes????
# def complete(tokens: List[str]) -> List[str]:
#     node = None
#     registry = CommandRegistry.build()

#     for token in tokens[:-1]:
#         if node is None:
#             node = registry.get(token)
#         else:
#             node = node.children.get(token)

#         if node is None:
#             return []

#     if node is None:
#         return list(registry.keys())

#     return [
#         name for name, child in node.children.items()
#         if not child.module_only or Dispatcher().current_module
#     ]