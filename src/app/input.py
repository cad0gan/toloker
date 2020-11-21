import curses
import asyncio
import contextlib
from typing import Union, Callable, Awaitable


InputCallback = Callable[[str], Awaitable]


class Input:
    def __init__(self, window: any) -> None:
        self._screen = window
        curses.curs_set(1)
        self._screen.keypad(True)
        self._result: str = str()
        self._x = 0
        self._y = curses.getsyx()[0]
        self._x_input: int = 0

    def _add(self, wch: str) -> None:
        self._result += wch
        self._x_input += len(wch)

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

    def _delete(self) -> None:
        with contextlib.suppress(IndexError):
            length = len(self._result)
            if self._x_input != length:
                result: list = list(self._result)
                result.pop(self._x_input)
                self._result = ''.join(result)
                if self._x_input > length:
                    self._x_input = length

    def _move(self) -> None:
        self._screen.move(self._y, self._x + self._x_input)

    def _draw(self) -> None:
        self._screen.move(self._y, self._x)
        self._screen.clrtoeol()
        self._screen.addstr(self._y, self._x, self._result)  # it moves the cursor
        self._screen.move(self._y, self._x + self._x_input)

    async def __call__(self, text: str) -> str:
        self._screen.addstr(self._y, self._x, text)
        self._x += len(text)
        while True:
            with contextlib.suppress(curses.error):
                length: int = len(self._result)
                wch: Union[str, int] = self._screen.get_wch()
                if isinstance(wch, str):
                    if wch == '\n':
                        break
                    elif wch == '':
                        self._remove()
                        self._draw()
                    else:
                        if self._x_input == length:
                            self._add(wch)
                        else:
                            self._insert(wch)
                        self._draw()
                else:
                    if length:
                        if wch == curses.KEY_LEFT:
                            self._x_input -= 1
                            if self._x_input <= 0:
                                self._x_input = 0
                            self._move()
                        elif wch == curses.KEY_RIGHT:
                            self._x_input += 1
                            if self._x_input > length:
                                self._x_input = length
                            self._move()
                        elif wch == curses.KEY_HOME:
                            self._x_input = 0
                            self._move()
                        elif wch == curses.KEY_END:
                            self._x_input = length
                            self._move()
                        elif wch == curses.KEY_DC:
                            self._delete()
                            self._draw()
            await asyncio.sleep(0.05)
        return self._result

    def __del__(self) -> None:
        self._screen.move(self._y + 1, 0)
        self._screen.refresh()
        self._screen.keypad(False)
        curses.curs_set(0)
        curses.flushinp()
