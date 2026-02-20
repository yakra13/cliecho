"""
TODO: docstring
"""
# import threading
# import time
# from pathlib import Path
# from queue import Empty, Queue
# from typing import List

# from dataclasses import dataclass, field
from typing import List
from core.cli_manager import CLIManager
from core.completer import Completer
# from core.dispatcher import Dispatcher
# from core.events import InputClosed, UserInterrupt
from core.module_loader import ModuleLoader
from shared.text.ansi import AnsiStyle
from shared.text.color import Color, lerp_color
from shared.formatter import style_text
# from shared.logger import EventLevel
from shared.module_logger import LOGGER
from core.config import CONFIG
from shared.task import Task

def _display_logo() -> None:
    text = """
 /▓▓▓▓▓▓▓                  /▓▓ /▓▓▓▓▓▓▓▓           /▓▓        /▓▓▓▓▓▓  
│ ▓▓__  ▓▓                │ ▓▓│ ▓▓_____/          │ ▓▓       /▓▓▓_  ▓▓ 
│ ▓▓  \ ▓▓  /▓▓▓▓▓▓   /▓▓▓▓▓▓▓│ ▓▓        /▓▓▓▓▓▓▓│ ▓▓▓▓▓▓▓ │ ▓▓▓▓╲ ▓▓ 
│ ▓▓▓▓▓▓▓/ /▓▓__  ▓▓ /▓▓__  ▓▓│ ▓▓▓▓▓    /▓▓_____/│ ▓▓__  ▓▓│ ▓▓ ▓▓ ▓▓ 
│ ▓▓__  ▓▓│ ▓▓▓▓▓▓▓▓│ ▓▓  │ ▓▓│ ▓▓__/   │ ▓▓      │ ▓▓  \ ▓▓│ ▓▓╲ ▓▓▓▓ 
│ ▓▓  \ ▓▓│ ▓▓_____/│ ▓▓  │ ▓▓│ ▓▓      │ ▓▓      │ ▓▓  │ ▓▓│ ▓▓ ╲ ▓▓▓ 
│ ▓▓  │ ▓▓│  ▓▓▓▓▓▓▓│  ▓▓▓▓▓▓▓│ ▓▓▓▓▓▓▓▓│  ▓▓▓▓▓▓▓│ ▓▓  │ ▓▓│  ▓▓▓▓▓▓/ 
│__/  │__/ ╲_______/ ╲_______/│________/ ╲_______/│__/  │__/ ╲______/  
"""
    logo = [list(line) for line in text.splitlines()]
    del logo[0]

    height = len(logo)
    width = len(logo[0])

    output = []
    for y in range(height):
        for x in range(width):
            c = logo[y][x]

            if x > 29:
                fade_color = lerp_color(Color.Black, Color(50, 0, 0), y / (height - 1))
                output.append(style_text(c, fade_color, Color(50, 0, 0), [AnsiStyle.BOLD]))
            else:
                fade_color = lerp_color(Color.Red, Color(50, 0, 0), y / (height - 1))
                output.append(style_text(c, fade_color, None, [AnsiStyle.BOLD]))

        output.append("\n")
    
    output = "".join(output)
    LOGGER.console_raw(output)
    # LOGGER.console_raw('\033[8A\033[K' + output)

# █  Full block
# ▓  Dark shade
# ▒  Medium shade
# ░  Light shade
# ▏ ▎ ▍ ▌ ▋ ▊ ▉ █
# ▁ ▂ ▃ ▄ ▅ ▆ ▇ █
# ─  Horizontal
# │  Vertical
# ┌  Top-left
# ┐  Top-right
# └  Bottom-left
# ┘  Bottom-right
# ├  Left tee
# ┤  Right tee
# ┬  Top tee
# ┴  Bottom tee
# ┼  Cross
# ═  ║    ╱   ╲
# ╔  ╗
# ╚  ╝
# ╠  ╣
# ╦  ╩
# ╬
# ╓ ╖ ╙ ╜
# ╒ ╕ ╘ ╛
# ╞ ╡ ╤ ╧ ╟ ╢


def _load(tasks: List[Task]) -> None:


    for task in tasks:
        LOGGER.console_raw(f"{task.name}...")
        result = task.execute()

        if not result:
            pass


    # Load Configuration
    LOGGER.console_raw("Loading configuration.")
    CONFIG.load_config_task()
    
    # Check for any errors in the configuration file
    err_count = len(CONFIG.errors)
    # Report any errors found
    if err_count > 0:
        LOGGER.console_raw(
            style_text(
                f"{err_count} error{'s' if err_count > 1 else ''} detected in configuration.", Color.Red))
        for i, err in enumerate(CONFIG.errors):
            LOGGER.console_raw(style_text(f"{i + 1}: ".rjust(5) + f"{err}", Color.Yellow))
    else:
        LOGGER.console_raw(f"Successfully loaded configuration.")

    # Validate/Create Paths
    LOGGER.console_raw("Validating and creating folder structure.")

    messages = CONFIG.build_workspace_task()

    for message in messages:
        LOGGER.console_raw(style_text(f"  {message}", Color.Yellow))

    # Setup commands tab completion
    LOGGER.console_raw("Setting up environment.")
    Completer().setup()

    # Discover available modules
    LOGGER.console_raw("Discovering modules.")
    ModuleLoader().discover()
    module_count = ModuleLoader().get_module_count()
    LOGGER.console_raw(
        style_text(f"  {module_count} module{'s' if module_count > 1 else ''} found.", Color.Cyan))

def _cleanup() -> None:
    # Perform clean up actions
    Completer().teardown()
    # TODO: delete .temp modules?

def main() -> None:
    """
    Docstring for main
    """

    _display_logo()
    # TODO: load stuff
    tasks: List[Task] = [
        Task("Load Configuration", CONFIG.load_config_task),
        Task("Create Workspace", CONFIG.build_workspace_task),
        Task("Setup Environment", Completer().setup)
    ]

    
    _load(tasks)
    
    # Start input loop
    CLIManager().run()

    _cleanup()


if __name__ == "__main__":
    main()
