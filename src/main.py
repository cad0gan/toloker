import pytz
import asyncio
import argparse
from tzlocal import get_localzone
from datetime import datetime
from pytoloka import Toloka
from pytoloka.exceptions import HttpError
from app import Window
from assigner import Assigner
from shortcuts import login

VERSION = '0.7.3'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')

    parser_assigner = subparsers.add_parser('assigner')
    parser_tasks = subparsers.add_parser('tasks')
    parser_tasks.add_argument('-l', '--list', action='store_true', help='show all tasks')
    parser_skills = subparsers.add_parser('skills')
    parser_skills.add_argument('-l', '--list', action='store_true', help='show all skills')
    parser_transactions = subparsers.add_parser('transactions')
    parser_transactions.add_argument('-l', '--list', action='store_true', help='show all transactions')
    parser_transactions.add_argument('-n', type=int)

    parser.add_argument('-v', '--version', action='store_true', help='show version and exit')
    args = parser.parse_args()

    if args.version:
        print(VERSION)
    elif args.subparser == 'assigner':
        try:
            toloka: Toloka = Toloka()
            if login(toloka):
                Window(Assigner(toloka))()
        except HttpError:
            exit(1)
    elif args.subparser == 'tasks':
        if args.list:
            try:
                toloka: Toloka = Toloka()
                if login(toloka):
                    tasks: list = asyncio.run(toloka.get_tasks())
                    for task in tasks:
                        string: str = str()
                        requester: str = task['requesterInfo']['name']['EN']  # requester
                        title: str = task['title']
                        string += f'\033[1m{requester}\033[0m. '
                        string += title
                        print(string)
            except HttpError:
                exit(1)
    elif args.subparser == 'skills':
        if args.list:
            try:
                toloka: Toloka = Toloka()
                if login(toloka):
                    skills: list = asyncio.run(toloka.get_skills())
                    for skill in skills:
                        string: str = str()
                        requester: str = skill['requesterName']['EN']
                        skill_name: str = skill['skillName']
                        value: int = skill['value']
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
    elif args.subparser == 'transactions':
        if args.list:
            try:
                toloka: Toloka = Toloka()
                if login(toloka):
                    tz = pytz.timezone(str(get_localzone()))
                    max_count: int = args.n if args.n is not None and args.n > 0 else 0
                    transactions: list = asyncio.run(toloka.get_transactions(max_count))
                    for transaction in transactions:
                        start_dt: datetime = transaction['startDate']
                        start_dt = start_dt.astimezone(tz)

                        payment_system: str = transaction['account']['paymentSystem']
                        amount: str = transaction['amount']
                        status: str = transaction['status']
                        print('{} {}\t{}\t{} $'.format(
                            start_dt.strftime('%d.%m.%y %H:%M'),
                            payment_system, status, amount
                        ))
            except HttpError:
                exit(1)
