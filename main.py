"""
TODO: docstring
"""
import threading
from queue import Empty, Queue
import time
from typing import List

from core.cli_manager import CLIManager
from core.completer import Completer
from core.dispatcher import Dispatcher
from core.events import InputClosed, UserInterrupt
from core.module_loader import ModuleLoader
from shared.module_logger import LOGGER

def display_logo() -> None:
    print("""\033[31m
╔═════╗
║   ╔╗║
║  ╔╩╬╩╗
╚═ ╩═╣ ║
     ╚═╝\033[0m""")
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
# ╞ ╡ ╤ ╧

def main() -> None:
    """
    Docstring for main
    """

    input_queue: Queue = Queue()
    # io_lock = threading.Lock()
    # print_event = threading.Event()
    # print_event.set()

    # LOGGER.io_lock = io_lock
    # LOGGER.print_event = print_event

    # Setup commands tab completion
    Completer().setup()

    # interface_manager.SetVerbosity()
    # interface_manager.SetFormat()

    # TODO: load stuff
    display_logo()
    ModuleLoader().discover()

    # Setup user input in its own thread allowing module threads to run independantly
    input_thread = threading.Thread(target=CLIManager().get_input, args=(input_queue,), daemon=True)
    input_thread.start()

    # Main program loop
    while True:
        # Update (check status, fill queues etc)
        Dispatcher().poll_jobs()
        
        # Get input is done in input_thread (CLIManager.get_input)
        # Consume input
        try:
            msg = input_queue.get(timeout=0.1)
        except Empty:
            # Timeout reached and no input was received
            continue
        
        # Handle input
        match msg:
            case InputClosed():
                # TODO: Input closed handle shutdown
                break
            case UserInterrupt():
                # TODO: ctrl C cancel running jobs?
                break # continue
            case str():
                # Process and handle user input
                tokens: List[str] = CLIManager().tokenize(msg)
                CLIManager().handle_command(tokens)
            case _:
                # unknown signal...
                break

        # Output to the CLI happens last, we should be guranteed 
        # that there is no user input entered into the console
        LOGGER.flush_console()


if __name__ == "__main__":
    main()
