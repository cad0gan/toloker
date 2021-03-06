import pytz
import asyncio
import argparse
from typing import Union
from decimal import Decimal
from datetime import datetime
from tzlocal import get_localzone
from termcolor import colored
from pytoloka import Toloka
from pytoloka.exceptions import HttpError, AccessDeniedError
from app import WindowAssigner
from version import VERSION
from assigner import Assigner
from shortcuts import login


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subparser')

    parser_assigner = subparsers.add_parser('assigner')
    parser_worker = subparsers.add_parser('worker')
    parser_tasks = subparsers.add_parser('tasks')
    parser_tasks.add_argument('-l', '--list', action='store_true', help='show all tasks')
    parser_skills = subparsers.add_parser('skills')
    parser_skills.add_argument('-l', '--list', action='store_true', help='show all skills')
    parser_skills.add_argument('-n', type=int, metavar='COUNT', help='skills count')
    parser_transactions = subparsers.add_parser('transactions')
    parser_transactions.add_argument('-l', '--list', action='store_true', help='show all transactions')
    parser_transactions.add_argument('-n', type=int, metavar='COUNT', help='transactions count')
    parser_history = subparsers.add_parser('history')
    parser_history.add_argument('-a', '--analytics', action='store_true', help='show analytics')

    parser.add_argument('-v', '--version', action='store_true', help='show version and exit')
    args = parser.parse_args()

    if args.version:
        print(VERSION)
    elif args.subparser == 'assigner':
        try:
            toloka: Toloka = Toloka()
            if login(toloka):
                WindowAssigner(Assigner(toloka))()
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
                        print('{}. {}'.format(colored(requester, attrs=['bold']), title))
            except HttpError:
                exit(1)
            except AccessDeniedError:
                print('Access denied')
                exit(1)
    elif args.subparser == 'worker':
        try:
            toloka: Toloka = Toloka()
            if login(toloka):
                worker: dict = asyncio.run(toloka.get_worker())
                login: str = worker['login']
                ban: bool = worker['systemBan']

                print('Login:', login)
                string: str = colored(str(ban).lower(), 'red') if ban else str(ban).lower()
                print(f'Ban: {string}')
                print('Balance: {} / {}'.format(
                    colored('{:.2f} $'.format(worker['blockedBalance']), 'grey'),
                    colored('{:.2f} $'.format(worker['balance']), 'green'),
                ))
                print('Rating: {}'.format(worker['rating']))
        except HttpError:
            exit(1)
    elif args.subparser == 'skills':
        if args.list:
            try:
                toloka: Toloka = Toloka()
                if login(toloka):
                    max_count: int = args.n if args.n is not None and args.n > 0 else 0
                    skills: list = asyncio.run(toloka.get_skills(max_count))
                    for skill in skills:
                        requester: str = skill['requesterName']['EN']
                        skill_name: str = skill['skillName']
                        value: int = skill['value']

                        string: str = str()
                        string += f'\033[1m{requester}\033[0m. '
                        string = '{}. {}'.format(colored(requester, attrs=['bold']), skill_name)
                        color: string = 'white'
                        if value <= 25:
                            color = 'red'
                        elif value <= 75:
                            color = 'yellow'
                        elif value <= 100:
                            color = 'green'
                        string += ': {}'.format(colored(str(value), color))
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
                        amount: Union[Decimal, str] = transaction['amount']
                        status: str = transaction['status']
                        amount = '{:.2f}'.format(amount)
                        amount = amount.rjust(5, ' ')
                        print('{} {}\t{}\t{} $'.format(
                            start_dt.strftime('%d.%m.%y %H:%M'),
                            payment_system, status, amount
                        ))
            except HttpError:
                exit(1)
    elif args.subparser == 'history':
        try:
            if args.analytics:
                toloka: Toloka = Toloka()
                if login(toloka):
                    analytics = asyncio.run(toloka.get_analytics())
                    print('Completed task: {}'.format(analytics['totalSubmittedAssignmentsCount']))
                    print('Rejected task: {}'.format(analytics['totalRejectedAssignmentsCount']))
                    print('Task under review: {}'.format(analytics['onReviewAssignmentsCount']))
                    print('Total sum earned since starting: {:.2f} $'.format(analytics['totalIncome']))
        except HttpError:
            exit(1)
