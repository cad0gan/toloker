import sys


class StdOut:
    @staticmethod
    def flush():
        sys.__stdout__.flush()

    @staticmethod
    def write(text):
        if text:
            if text == '\n':
                sys.__stdout__.write('\r')
            sys.__stdout__.write(text)

    def set(self):
        sys.stdout = self

    @staticmethod
    def unset():
        sys.stdout = sys.__stdout__
