import curses
from curses import textpad
import shlex
from pathlib import Path
from typing import Optional

from core.module_loader import ModuleLoader
from core.dispatcher import Dispatcher
from shared.module_base import ModuleBase

class CLI:
    def __init__(self, dispatcher: Dispatcher):
        self._dispatcher: Dispatcher = dispatcher
        self._interactive: bool = True

    def _get_prompt(self) -> str:
        module: Optional[ModuleBase] = self._dispatcher.current_module()
        return f'{module.name}> ' if module else '> '

    def _parse_input(self, text: str) -> list[str]:
        try:
            return shlex.split(text)
        except ValueError:
            print("[-] Input parse error.")
            return []

    def _show_help(self, args: list[str]) -> str:
        return ''

    def _curses_interface(self, stdscr: curses.window) -> None:
        # set up
        curses.curs_set(1) # show cursor
        stdscr.nodelay(True)
        curses.start_color()

        output_lines = []


        def redraw_all():
            stdscr.clear()
            stdscr.erase()
            
            h, w = stdscr.getmaxyx()

            max_output_lines = h -2
            
            start = max(0, len(output_lines) - max_output_lines)

            for i, line in enumerate(output_lines[start:start + max_output_lines]):
                stdscr.addstr(i, 0, line[:w - 1])
            
            stdscr.addstr(h -1, 0, "> ")
            # stdscr.hline(h - 2, 0, u'\u2550', w) # curses.ACS_HLINE
            stdscr.addstr(h - 2, 0, u'\u2550' * w)
            stdscr.refresh()

            return h, w
        
        h, w = redraw_all()

        #main loop
        while True:
            # ch = stdscr.getch()
            # if ch == curses.KEY_RESIZE:
            #     curses.resize_term(*stdscr.getmaxyx())
            #     h, w = redraw_all()
            #     continue

            # if ch != -1:
            #     continue

            # stdscr.nodelay(False)

            input_window = curses.newwin(1, w - 2, h - 1, 2)
            # input_window.erase()
            input_window.keypad(True)

            box = textpad.Textbox(input_window, insert_mode=True)
            

            # curses.echo()

            def validator(ch):
                nonlocal h, w
                if ch == curses.KEY_RESIZE:
                    curses.resize_term(*stdscr.getmaxyx())
                    h, w = redraw_all()
                    input_window.resize(1, max(1, w - 2))
                    return -1
                return ch
            
            user_input = box.edit(validator).strip()
            # curses.noecho()

            stdscr.nodelay(True)

            if user_input == "quit":
                break

            output_lines.append(f"{user_input}")

            h, w = redraw_all()



            # stdscr.clear()

            # input_window.addstr(0, 0, "> ")
            # input_window.refresh()
            # edit_window.refresh()
            # stdscr.refresh()
            # height, width = stdscr.getmaxyx()
            # input_window.erase()

            # edit_window = curses.newwin(1, width - 2, height - 1, 2)
            # box = textpad.Textbox(edit_window, insert_mode=True)

            # input_window.refresh()

            # user_input = box.edit().strip() # can pass validator to edit

            # if user_input == "quit":
            #     break


            # curses.napms(20)
            
            # stdscr.addstr(0, 0, "test curses")
            # curses.echo()
            # user_input = input_window.getstr(0, 2).decode()
            # curses.noecho()

            
            # stdscr.addstr(height - 2, 0, f"{user_input}")
            # stdscr.refresh()
            # stdscr.getch()
            # key = stdscr.getch()


    def run(self):
        if self._interactive:
            curses.wrapper(self._curses_interface)
        return
        while True:
            try:
                user_input = input(self._get_prompt())
            except (EOFError, KeyboardInterrupt):
                print()
                return

            # Skip blank lines
            if not user_input.strip():
                continue

            cmd, *args = self._parse_input(user_input)

            cmd = cmd.lower()

            # Central routing
            if cmd == "exit" or cmd == "quit":
                return
            elif cmd == "help":
                self._show_help(args)
            else:
                # Everything else gets sent to the dispatcher
                self._dispatcher.handle_command(cmd, args)

            # user_input = input(self._get_prompt())
            # show modules
            # search "*" (need tags or search name and description?)
            # help
            # use "module"
            # describe "module"
            # exit
            # > show options
            # > set "option" "value"
            # > unset "option"
            # > run
            # > info
            # > save settings "label" (store modules current settings value)
            # > show settings (shows saved settings for current module)
            # > load "label"
            # > back
        pass


# example
'''
dispatcher = Dispatcher()

cli = CLI(dispatcher)

curses.wrapper(cli.run)



def main():
    dispatcher = Dispatcher()
    dispatcher.register_module("mod", ExampleModule())

    if "--curses" in sys.argv:
        curses_cli = CursesCLI(dispatcher)
        curses.wrapper(curses_cli.run)
    else:
        std_cli = StandardCLI(dispatcher)
        std_cli.run()
'''