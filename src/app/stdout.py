import sys


class StdOut:
    def __enter__(self):
        sys.stdout = self

    def __exit__(self, *args, **kwargs):
        sys.stdout = sys.__stdout__

    @staticmethod
    def flush() -> None:
        sys.__stdout__.flush()

    @staticmethod
    def write(text: str) -> None:
        if text:
            if text == '\n':
                sys.__stdout__.write('\r')
            sys.__stdout__.write(text)
