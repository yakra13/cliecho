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

def display_logo() -> None:
    print("""
╔══════════╗
║          ║
║          ║
║          ║
║          ║
║        ╔╗║
║       ╔╩╬╩╗
╚═══════╩═╣ ║
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
    # Setup commands tab completion
    Completer.setup()

    # interface_manager.SetVerbosity()
    # interface_manager.SetFormat()

    # TODO: load stuff
    display_logo()
    ModuleLoader().discover()

    input_thread = threading.Thread(target=CLIManager().get_input,
                                    args=(input_queue,),
                                    daemon=True)
    input_thread.start()

    while True:
        Dispatcher().poll_jobs()
        # other stuff?
        try:
            cmd = input_queue.get()
        except Empty:
            pass
        else:
            if cmd == "__EOF__":
                break

            tokens: List[str] = CLIManager().tokenize(cmd)
            CLIManager().handle_command(tokens)

        
        time.sleep(0.05)


if __name__ == "__main__":
    main()
