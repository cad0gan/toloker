import asyncio
import argparse
from pytoloka import Toloka
from pytoloka.exceptions import HttpError
from config import Config
from window import Window
from shortcuts import login
from auto_accept import AutoAccept

VERSION = '0.2.0'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('action', nargs='?', help='[accept]')
    parser.add_argument('-l', '--list-tasks', action='store_true', help='show all tasks')
    parser.add_argument('-s', '--list-skills', action='store_true', help='show your skills')
    parser.add_argument('-v', '--version', action='store_true', help='show version and exit')
    args = parser.parse_args()

    if args.list_tasks:
        try:
            toloka = Toloka()
            if login(toloka):
                tasks = asyncio.run(toloka.get_tasks())
                for task in tasks:
                    print(task['title'])
        except HttpError:
            exit(1)
    elif args.list_skills:
        try:
            toloka = Toloka()
            if login(toloka):
                skills = asyncio.run(toloka.get_skills())
                for skill in skills:
                    print('{}: {}'.format(skill['skillName'], skill['value']))
        except HttpError:
            exit(1)
    elif args.version:
        print(VERSION)
    else:
        try:
            toloka = Toloka()
            if login(toloka):
                Window(AutoAccept(toloka))()
        except HttpError:
            exit(1)
