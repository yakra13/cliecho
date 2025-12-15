"""
TODO: docstring
"""
import threading
from queue import Empty, Queue
import time

from core.completer import Completer
from core.dispatcher import Dispatcher
from core.interface_manager import InterfaceManager
from core.module_loader import ModuleLoader

def display_logo() -> None:
    print("Thingy!")

def main() -> None:
    """
    Docstring for main
    """
    # TODO: load stuff

    module_loader = ModuleLoader()
    dispatcher = Dispatcher()
    interface_manager = InterfaceManager()
    input_queue: Queue = Queue()
    # Setup commands tab completion
    Completer.setup()
    # interface_manager.SetVerbosity()
    # interface_manager.SetFormat()

    display_logo()
    module_loader.discover()

    input_thread = threading.Thread(target=InterfaceManager.get_input,
                                    args=(input_queue,),
                                    daemon=True)
    input_thread.start()

    while True:
        dispatcher.poll_jobs()
        # other stuff?
        try:
            cmd = input_queue.get_nowait()
        except Empty:
            pass
        else:
            if cmd == "__EOF__":
                break

            token_list = interface_manager.parse_input(cmd)
            interface_manager.handle_command(command, args)

            if interface_manager.is_top_level_command(command):
            else:
                dispatcher.handle_command(command, args)
        
        time.sleep(0.05)


if __name__ == "__main__":
    main()
