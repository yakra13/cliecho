"""
TODO: docstring
"""
import threading
import time
from pathlib import Path
from queue import Empty, Queue
from typing import List

from core.cli_manager import CLIManager
from core.completer import Completer
# from core.dispatcher import Dispatcher
# from core.events import InputClosed, UserInterrupt
from core.module_loader import ModuleLoader
from shared.ansi import AnsiStyle
from shared.color import Color, lerp_color
from shared.formatter import style_text
from shared.module_logger import LOGGER

def display_logo() -> None:
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

def main() -> None:
    """
    Docstring for main
    """

    display_logo()
    # TODO: load stuff
    # Load Configuration
    
    # Setup commands tab completion
    Completer().setup()

    # Discover available modules
    ModuleLoader().discover()

    # Start input loop
    CLIManager().run()

    # Perform clean up actions
    Completer().teardown()
    # TODO: delete .temp modules?


if __name__ == "__main__":
    main()
