import curses
import signal
import asyncio
from threading import Thread
from app.stdout import StdOut


class Window:
    def __init__(self, worker):
        self._worker = worker
        self._screen = None
        self._stdout = StdOut()
        self._thread = Thread(target=self._handle_keypress)

    def _handle_keypress(self):
        while True:
            ch = self._screen.getch()
            if ch == ord('q'):
                self._worker.exit()
                break
            elif ch == ord('s'):
                self._worker.pause()

    def __call__(self):
        self._screen = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(False)
        try:
            curses.start_color()
            curses.use_default_colors()
        except curses.error:
            pass
        self._screen.clear()
        self._stdout.set()
        signal.signal(signal.SIGINT, lambda signum, frame: None)
        self._thread.start()
        asyncio.run(self._worker())

    def __del__(self):
        self._thread.join()
        curses.endwin()
        self._stdout.unset()
