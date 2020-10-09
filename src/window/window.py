import curses
import asyncio
from window.stdout import StdOut
from auto_accept import AutoAccept


class Window:
    def __init__(self, toloka):
        self._toloka = toloka
        self._screen = None
        self._stdout = StdOut()

    def __call__(self):
        self._screen = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.start_color()
        if curses.can_change_color():
            curses.use_default_colors()
        curses.curs_set(False)
        self._screen.clear()
        self._stdout.set()
        asyncio.run(AutoAccept(self._toloka)())

    def __del__(self):
        curses.endwin()
        self._stdout.unset()
