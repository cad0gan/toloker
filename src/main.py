import asyncio
import argparse
from pytoloka import Toloka
from config import Config
from window import Window
from auto_accept import AutoAccept

VERSION = '0.0.1'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('action', nargs='?', help='[accept]')
    parser.add_argument('-v', '--version', action='store_true', help='show version and exit')
    args = parser.parse_args()

    if args.version:
        print(VERSION)
    else:
        config = Config()
        toloka = Toloka()
        if asyncio.run(toloka.login(config.username, config.password)):
            Window(AutoAccept(toloka))()
