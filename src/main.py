import asyncio
import argparse
from pytoloka import Toloka
from pytoloka.exceptions import HttpError
from app import Window
from assigner import Assigner
from shortcuts import login

VERSION = '0.3.0'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')

    parser_assigner = subparsers.add_parser('assigner')

    parser_tasks = subparsers.add_parser('tasks')
    parser_tasks.add_argument('-l', '--list-tasks', action='store_true', help='show all tasks')

    parser_skills = subparsers.add_parser('skills')
    parser_skills.add_argument('-l', '--list-skills', action='store_true', help='show all skills')

    parser.add_argument('-v', '--version', action='store_true', help='show version and exit')
    args = parser.parse_args()

    if args.version:
        print(VERSION)
    elif args.subparser == 'tasks':
        if args.list_tasks:
            try:
                toloka = Toloka()
                if login(toloka):
                    tasks = asyncio.run(toloka.get_tasks())
                    for task in tasks:
                        string: str = str()
                        title = task['title']
                        requester = task['requesterInfo']['name']['EN']  # requester
                        string += f'\033[1m{requester}\033[0m. '
                        string += title
                        print(string)
            except HttpError:
                exit(1)
    elif args.subparser == 'skills':
        if args.list_skills:
            try:
                toloka = Toloka()
                if login(toloka):
                    skills = asyncio.run(toloka.get_skills())
                    for skill in skills:
                        print('{}: {}'.format(skill['skillName'], skill['value']))
            except HttpError:
                exit(1)
    elif args.subparser == 'assigner':
        try:
            toloka = Toloka()
            if login(toloka):
                Window(Assigner(toloka))()
        except HttpError:
            exit(1)
