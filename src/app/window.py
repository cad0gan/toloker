import sys
import time
import curses
import signal
import asyncio
import contextlib
from typing import Union
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

    async def input(self, text: str) -> str:
        result: str = str()
        self._input = True
        curses.curs_set(True)
        self._screen.keypad(True)

        x_input: int = 0
        y, x = curses.getsyx()
        self._screen.addstr(y, x, text)
        x += len(text)
        while True:
            with contextlib.suppress(curses.error):
                wch: Union[str, int] = self._screen.get_wch()
                if isinstance(wch, str):
                    x_old: int = 0
                    if wch == '\n':
                        sys.stdout.write('\r\n')
                        break
                    if x_input == len(result):
                        result += wch
                        x_input += len(wch)
                    else:
                        result_list = list(result)
                        result_list.insert(x_input, wch)
                        result = ''.join(result_list)
                        x_old = curses.getsyx()[1]

                    self._screen.move(y, x)
                    self._screen.clrtoeol()
                    self._screen.addstr(y, x, result)  # moved cursor
                    if x_old:
                        x_input += 1
                        self._screen.move(y, x_old + 1)
                else:
                    if len(result):
                        if wch == curses.KEY_LEFT:
                            x_input -= 1
                            if x_input <= 0:
                                x_input = 0
                        elif wch == curses.KEY_RIGHT:
                            x_input += 1
                            if x_input >= len(result):
                                x_input = len(result) - 1
                        self._screen.move(y, x + x_input)

            await asyncio.sleep(0.05)

        self._screen.keypad(False)
        curses.curs_set(False)
        curses.flushinp()
        self._input = False
        return result

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
