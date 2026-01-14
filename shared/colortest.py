import os
import sys
import time
def supports_truecolor() -> bool:
    return os.environ.get("COLORTERM") in {"truecolor", "24bit"}

if supports_truecolor():

    # check if terminal is tty as well as the os my support but the terminal may be remote etc
    # sys.stdout.isatty()

    print("Should support it.")
    r = 0
    g = 0
    b = 255
    direction = False
    while True:
        if direction:
            r -= 1
            b += 1
        else:
            r += 1
            b -= 1
            # r = min(r + 1, 255)
            # b = max(b - 1, 0)
        if r <= 0:
            r = 0
            b = 255
            direction = not direction
        elif r >= 255:
            r = 255
            b = 0
            direction = not direction
        fg = f"\033[1;3;4;5;9;38;2;{str(r)};{str(g)};{str(b)}m"
        #foreground rgb is 38;2;r;g;b
        #background is 48;2;r;g;b
        #styles 0-9; (0 -> reset)
        #\033[{styles}{fg}{bg}
        #\033[1;3;38;2;r;g;b;48;2;r;g;bm   bold italic fg bg colored

        # print(f"\r{fg}This is a test.\033[0m")
        #\r return carriage to write over
        sys.stdout.write(f"\r{fg}This is a test.\033[0m")
        sys.stdout.flush()
        time.sleep(0.01)
        # input()
        # print('''
        # ┌────────┬────────┐
        # │{fg}Column 1\033[0m│\033[1mColumn 2\033[0m│
        # ├────────┼────────┤
        # │Value 1 │ Value 2│
        # ├────────┼────────┤
        # │\033[47;30mValue 3 \033[0m│\033[47;30m Value 4\033[0m│
        # └────────┴────────┘
        # ''')