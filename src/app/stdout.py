import sys


class StdOut:
    @staticmethod
    def flush() -> None:
        sys.__stdout__.flush()

    @staticmethod
    def write(text: str) -> None:
        if text:
            if text == '\n':
                sys.__stdout__.write('\r')
            sys.__stdout__.write(text)

    def set(self) -> None:
        sys.stdout = self

    @staticmethod
    def unset() -> None:
        sys.stdout = sys.__stdout__
