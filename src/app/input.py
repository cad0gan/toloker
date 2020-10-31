import sys
import curses
import asyncio
import contextlib
from typing import Union


class Input:
    def __init__(self, screen: any) -> None:
        self._screen = screen
        curses.curs_set(1)
        self._screen.keypad(True)
        self._result: str = str()
        self._x, self._y = curses.getsyx()
        self._x_input: int = 0

    def _remove(self) -> None:
        with contextlib.suppress(IndexError):
            if self._x_input:
                result: list = list(self._result)
                result.pop(self._x_input - 1)
                self._result = ''.join(result)
                self._x_input -= 1

    def _insert(self, wch: str) -> None:
        result: list = list(self._result)
        result.insert(self._x_input, wch)
        self._result = ''.join(result)
        self._x_input += 1

    async def __call__(self, text: str) -> str:
        self._screen.addstr(self._y, self._x, text)
        self._x += len(text)
        while True:
            with contextlib.suppress(curses.error):
                length: int = len(self._result)
                wch: Union[str, int] = self._screen.get_wch()
                if isinstance(wch, str):
                    if wch == '\n':
                        sys.stdout.write('\r\n')
                        break
                    elif wch == '':
                        self._remove()
                    else:
                        if self._x_input == length:
                            self._result += wch
                            self._x_input += len(wch)
                        else:
                            self._insert(wch)

                    self._screen.move(self._y, self._x)
                    self._screen.clrtoeol()
                    self._screen.addstr(self._y, self._x, self._result)  # moved cursor
                    self._screen.move(self._y, self._x + self._x_input)
                else:
                    if length:
                        if wch == curses.KEY_LEFT:
                            self._x_input -= 1
                            if self._x_input <= 0:
                                self._x_input = 0
                        elif wch == curses.KEY_RIGHT:
                            self._x_input += 1
                            if self._x_input > length:
                                self._x_input = length
                        self._screen.move(self._y, self._x + self._x_input)
            await asyncio.sleep(0.05)
        return self._result

    def __del__(self) -> None:
        self._screen.keypad(False)
        curses.curs_set(0)
        curses.flushinp()
