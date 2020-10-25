import time
import curses
import signal
import asyncio
from threading import Thread
from app.stdout import StdOut
from telegram_bot import TelegramBot


class Window:
    def __init__(self, worker: any) -> None:
        self._worker: any = worker
        self._screen: any = None
        self._stdout: StdOut = StdOut()
        self._thread: Thread = Thread(target=self._handle_keypress)
        self._telegram_bot: TelegramBot = TelegramBot()
        self._input: bool = False

    def input(self, text: str) -> str:
        self._input = True
        curses.nocbreak()
        curses.echo()
        curses.curs_set(True)
        self._screen.nodelay(False)

        y, x = curses.getsyx()
        self._screen.addstr(y, x, text)
        result: bytes = self._screen.getstr()

        self._screen.nodelay(True)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(False)
        curses.flushinp()
        self._input = False
        return result.decode('utf-8')

    def _handle_keypress(self) -> None:
        while True:
            if not self._input:
                ch: str = self._screen.getch()
                if ch == ord('q'):
                    self._worker.exit()
                    self._telegram_bot.exit()
                    break
                elif ch == ord('s'):
                    self._worker.pause()
            time.sleep(0.5)

    def __call__(self) -> None:
        self._screen: any = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(False)
        try:
            curses.start_color()
            curses.use_default_colors()
        except curses.error:
            pass
        self._screen.clear()
        self._screen.nodelay(True)
        self._stdout.set()
        signal.signal(signal.SIGINT, lambda signum, frame: None)
        self._thread.start()

        async def run():
            await asyncio.gather(self._worker(self.input), self._telegram_bot())
        asyncio.run(run())

    def __del__(self) -> None:
        self._thread.join()
        curses.endwin()
        self._stdout.unset()
