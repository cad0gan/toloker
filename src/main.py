import asyncio
import argparse
from pytoloka import Toloka
from pytoloka.exceptions import HttpError
from app import Window
from assigner import Assigner
from shortcuts import login

VERSION = '0.4.0'

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
                        requester = task['requesterInfo']['name']['EN']  # requester
                        title = task['title']
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
                        string: str = str()
                        requester = skill['requesterName']['EN']
                        skill_name = skill['skillName']
                        value = skill['value']
                        string += f'\033[1m{requester}\033[0m. '
                        string += f'{skill_name}: '
                        if value <= 25:
                            string += '\33[31m'  # red
                        elif value <= 75:
                            string += '\33[33m'  # yellow
                        elif value <= 100:
                            string += '\33[32m'  # red
                        string += f'{value}\33[0m'
                        print(string)
            except HttpError:
                exit(1)
    elif args.subparser == 'assigner':
        try:
            toloka = Toloka()
            if login(toloka):
                Window(Assigner(toloka))()
        except HttpError:
            exit(1)
