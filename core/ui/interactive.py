# import curses

# class Interactive:
#     def __init__(self):

#         pass

#     def _gui(self, stdscr: curses.window) -> None:
#         curses.curs_set(1)
#         stdscr.nodelay(False)
#         stdscr.keypad(True)

#         input_history: list[str] = []
#         input_buffer: list[str] = []
#         cursor_pos = 0

#         output_lines = []

#         def redraw() -> tuple[int, int]:
#             stdscr.clear()
#             h, w = stdscr.getmaxyx()

#             # draw output (scrollback)
#             max_out = h - 2
#             start = max(0, len(output_lines) - max_out)
#             for i, line in enumerate(output_lines[start:]):
#                 stdscr.addstr(i, 0, line[:w-1])

#             # draw prompt
#             stdscr.addstr(h - 1, 0, "> ")

#             # draw input buffer
#             visible = "".join(input_buffer)
#             stdscr.addstr(h - 1, 2, visible[:w-3])

#             # move cursor
#             stdscr.move(h - 1, 2 + cursor_pos)

#             stdscr.refresh()
#             return h, w

#         h, w = redraw()

#         while True:
#             ch = stdscr.getch()

#             if ch == curses.KEY_RESIZE:
#                 redraw()
#                 continue

#             # ENTER
#             if ch in (curses.KEY_ENTER, 10, 13):
#                 user_input = "".join(input_buffer)
#                 input_history.append(user_input)
#                 input_buffer.clear()
#                 cursor_pos = 0

#                 # process user_input to dispatcher

#                 h, w = redraw()
#                 continue

#             # LEFT ARROW
#             if ch == curses.KEY_LEFT:
#                 if cursor_pos > 0:
#                     cursor_pos -= 1
#                 h, w = redraw()
#                 continue

#             # RIGHT ARROW
#             if ch == curses.KEY_RIGHT:
#                 if cursor_pos < len(input_buffer):
#                     cursor_pos += 1
#                 h, w = redraw()
#                 continue

#             # BACKSPACE (127 or curses.KEY_BACKSPACE)
#             if ch in (curses.KEY_BACKSPACE, 127):
#                 if cursor_pos > 0:
#                     input_buffer.pop(cursor_pos - 1)
#                     cursor_pos -= 1
#                 h, w = redraw()
#                 continue

#             # DELETE key
#             if ch == curses.KEY_DC:
#                 if cursor_pos < len(input_buffer):
#                     input_buffer.pop(cursor_pos)
#                 h, w = redraw()
#                 continue

#             # HOME
#             if ch == curses.KEY_HOME:
#                 cursor_pos = 0
#                 h, w = redraw()
#                 continue

#             # END
#             if ch == curses.KEY_END:
#                 cursor_pos = len(input_buffer)
#                 h, w = redraw()
#                 continue

#             # Printable characters only
#             if isinstance(ch, int) and 32 <= ch <= 126:
#                 input_buffer.insert(cursor_pos, chr(ch))
#                 cursor_pos += 1
#                 h, w = redraw()
#                 continue

#     def run(self):
#         curses.wrapper(self._gui)
