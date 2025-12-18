"""
TODO: docstring
"""
import threading
from queue import Empty, Queue
import time
from typing import List

from core.completer import Completer
from core.dispatcher import Dispatcher
from core.cli_manager import CLIManager
from core.module_loader import ModuleLoader
from shared.module_logger import LOGGER

def display_logo() -> None:
    print("""
╔══════════╗
║          ║
║          ║
║          ║
║          ║
║        ╔╗
║       ╔╩╬╩╗
╚══════ ╩═╣ ║
          ╚═╝
\033[31m
\033[0m     
""")
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
    io_lock = threading.Lock()
    print_event = threading.Event()
    print_event.set()

    LOGGER.io_lock = io_lock
    LOGGER.print_event = print_event

    # Setup commands tab completion
    Completer.setup()

    # interface_manager.SetVerbosity()
    # interface_manager.SetFormat()

    # TODO: load stuff
    display_logo()
    ModuleLoader().discover()

    input_thread = threading.Thread(target=CLIManager().get_input,
                                    args=(input_queue, io_lock, print_event,),
                                    daemon=True)
    input_thread.start()

    while True:
        # LOGGER.console_error("error message")
        Dispatcher().poll_jobs()
        # other stuff?
        try:
            # Get user input
            cmd = input_queue.get(timeout=0.1)
        except Empty:
            pass
        else:
            if cmd == "__EOF__":
                break
            # Process and handle user input
            tokens: List[str] = CLIManager().tokenize(cmd)
            CLIManager().handle_command(tokens)

        
        # time.sleep(0.05)


if __name__ == "__main__":
    main()
