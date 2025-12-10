"""
Docstring for core.command_tree
"""
from enum import Enum, auto
from core.interface_manager import InterfaceManager

class Commands(Enum):
    SHOW = auto()
    MODULES = auto()
    OPTIONS = auto()

class CommandMeta(Enum):
    ACTION = auto()

command_tree = {
    Commands.SHOW: {
        Commands.MODULES: {CommandMeta.ACTION: InterfaceManager.run},
        Commands.OPTIONS: {"requires_module": True, CommandMeta.ACTION: InterfaceManager.run}
    }
}