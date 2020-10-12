import asyncio
import argparse
from pytoloka import Toloka
from pytoloka.exceptions import HttpError
from config import Config
from window import Window
from auto_accept import AutoAccept

VERSION = '0.0.1'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('action', nargs='?', help='[accept]')
    parser.add_argument('-l', '--list-tasks', action='store_true', help='show all tasks')
    parser.add_argument('-v', '--version', action='store_true', help='show version and exit')
    args = parser.parse_args()

    if args.list_tasks:
        config = Config()
        toloka = Toloka()
        login = asyncio.run(toloka.login(config.username, config.password))
        if login:
            tasks = asyncio.run(toloka.get_tasks())
            for task in tasks:
                print(task['title'])
        else:
            print('You are not logged in!')
    elif args.version:
        print(VERSION)
    else:
        config = Config()
        toloka = Toloka()
        try:
            login = asyncio.run(toloka.login(config.username, config.password))
            if login:
                Window(AutoAccept(toloka))()
            else:
                print('You are not logged in!')
        except HttpError:
            exit(1)
