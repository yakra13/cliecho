"""
TODO: docstring
"""
from pathlib import Path
import threading
from queue import Empty, Queue
import time
from typing import List

from core.cli_manager import CLIManager
from core.completer import Completer
from core.dispatcher import Dispatcher
from core.events import InputClosed, UserInterrupt
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

    input_queue: Queue = Queue() # TODO: wont need this
    # io_lock = threading.Lock()
    # print_event = threading.Event()
    # print_event.set()

    # LOGGER.io_lock = io_lock
    # LOGGER.print_event = print_event


    # interface_manager.SetVerbosity()
    # interface_manager.SetFormat()

    display_logo()
    # TODO: load stuff
    # Setup commands tab completion
    Completer().setup()
    ModuleLoader().discover()

    # Start input loop
    CLIManager().run()

    # Perform clean up actions
    Completer().teardown()

    #TODO: remove below
    # Setup user input in its own thread allowing module threads to run independantly
    input_thread = threading.Thread(target=CLIManager().get_input, args=(input_queue,), daemon=True)
    input_thread.start()


    ctrlc = False
    # Main program loop
    while True:
        try:
            # Update (check status, fill queues etc)
            Dispatcher().poll_jobs()
            
            # Get input is done in input_thread (CLIManager.get_input)
            # Consume input
            if not ctrlc:
                try:
                    msg = input_queue.get(timeout=0.1)
                except Empty:
                    # Timeout reached and no input was received
                    continue
            else:
                ctrlc = False
                msg = UserInterrupt()

            # Handle input
            match msg:
                case InputClosed():
                    # TODO: Input closed handle shutdown
                    break
                case UserInterrupt():
                    # TODO: ctrl C cancel running jobs?
                    LOGGER.console_raw("Ctrl C was captured!\n")
                    continue # continue
                case str():
                    # Process and handle user input
                    tokens: List[str] = CLIManager().tokenize(msg)
                    CLIManager().handle_command(tokens)
                case _:
                    # unknown signal...
                    break

            # Output to the CLI happens last, we should be guranteed 
            # that there is no user input entered into the console
            # LOGGER.flush_console()
            Completer.teardown() # TODO: place this where exit cleanup happens
        except KeyboardInterrupt:
            ctrlc = True
            continue


if __name__ == "__main__":
    main()
