import time
import curses
import signal
import asyncio
import contextlib
from typing import NoReturn
from threading import Thread
from assigner import Assigner
from telegram_bot import TelegramBot
from app.input import Input
from app.stdout import StdOut


class Window:
    def __init__(self, worker: any) -> None:
        self._worker: any = worker
        self._worker.input = self.input
        self._window: any = None
        self._window_input: any = None
        self._stdout: StdOut = StdOut()
        self._thread: Thread = Thread(target=self._handle_keypress)
        self._input: bool = False

    async def _run(self) -> NoReturn:
        raise NotImplementedError('._run() must be overridden.')

    def _handle_keypress(self) -> NoReturn:
        raise NotImplementedError('._handle_keypress() must be overridden.')

    ####################################################################################################################

    async def input(self, text: str) -> str:
        self._input = True
        _input = Input(self._window_input)
        try:
            result: str = await _input(text)
        finally:
            self._input = False
        return result

    def __call__(self) -> None:
        self._window = curses.initscr()
        self._window_input = curses.newwin(*self._window.getmaxyx())
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        with contextlib.suppress(curses.error):
            curses.start_color()
            curses.use_default_colors()
        self._window.clear()
        self._window_input.nodelay(True)
        signal.signal(signal.SIGINT, lambda signum, frame: None)
        with self._stdout:
            self._thread.start()
            asyncio.run(self._run())
            self._thread.join()

    def __del__(self) -> None:
        with contextlib.suppress(curses.error):
            curses.endwin()


class WindowAssigner(Window):
    def __init__(self, worker: Assigner):
        super(WindowAssigner, self).__init__(worker)
        self._telegram_bot: TelegramBot = TelegramBot()

    async def _run(self) -> None:
        await asyncio.gather(self._worker(), self._telegram_bot())

    def _handle_keypress(self) -> None:
        while True:
            if not self._input:
                ch: str = self._window_input.getch()
                if ch == ord('q'):
                    self._worker.exit()
                    self._telegram_bot.exit()
                    break
                elif ch == ord('s'):
                    self._worker.pause()
                elif ch == ord('t'):
                    self._worker.print_stats()
            time.sleep(0.5)
