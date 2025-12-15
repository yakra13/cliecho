"""
TODO: docstring
"""
import threading
from queue import Empty, Queue
import time
from typing import List

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

    # module_loader = ModuleLoader()
    dispatcher = Dispatcher()
    interface_manager = InterfaceManager()
    input_queue: Queue = Queue()
    # Setup commands tab completion
    Completer.setup()
    # interface_manager.SetVerbosity()
    # interface_manager.SetFormat()

    display_logo()
    ModuleLoader().discover()
    print(ModuleLoader().get_modules_list())
    print("asdasd asd asda dsa ")

    input_thread = threading.Thread(target=interface_manager.get_input,
                                    args=(input_queue,),
                                    daemon=True)
    input_thread.start()

    while True:
        dispatcher.poll_jobs()
        # other stuff?
        try:
            cmd = input_queue.get()
        except Empty:
            pass
        else:
            if cmd == "__EOF__":
                break

            tokens: List[str] = interface_manager.tokenize(cmd)
            interface_manager.handle_command(tokens)

        
        time.sleep(0.05)


if __name__ == "__main__":
    main()
