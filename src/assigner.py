import sys
import asyncio
from typing import Union
from termcolor import colored
from pytoloka import Toloka
from pytoloka.exceptions import HttpError, AccessDeniedError
from notify import Notify
from app.input import InputCallback


class Assigner:
    def __init__(self, toloka: Toloka) -> None:
        self._toloka: Toloka = toloka
        self._input: Union[InputCallback, None] = None
        self._exit: bool = False
        self._pause: int = 0
        self._stats: dict[str, int] = dict(requests=0, errors=0, activated_tasks=0, activated_errors=0)

    @property
    def input(self) -> Union[InputCallback, None]:
        return self._input

    @input.setter
    def input(self, arg: InputCallback):
        self._input = arg

    def exit(self) -> None:
        if not self._exit:
            print('Exiting...')
            self._exit = True

    def pause(self) -> None:
        if self._pause == 0:
            print('Pausing...')
            sys.stdout.write('\033[F')
            sys.stdout.write('\033[K')
            self._pause = 1
        elif self._pause == 2:
            print('Unpause')
            self._pause = False

    def _print_stats(self, tasks: int):
        print('Requests: {}|{}. Activated tasks: {}|{}. Total tasks: {}.'.format(
            colored(str(self._stats['requests']), 'green'), colored(str(self._stats['errors']), 'red'),
            colored(str(self._stats['activated_tasks']), 'green'), colored(str(self._stats['activated_errors']), 'red'),
            tasks
        ))
        sys.stdout.write('\033[F')
        sys.stdout.write('\033[K')

    async def _assign_task(self, task: dict) -> None:
        title: str = task['title']
        if task['projectMetaInfo'].get('bookmarked'):
            # if task['pools'][0].get('activeAssignments'):
            #     print('Active task: {}'.format(title))
            if not task['pools'][0].get('activeAssignments'):
                pool_id: int = task['pools'][0]['id']
                ref_uuid: str = task['refUuid']

                print(f'Activating the task: {title}')
                result: dict = await self._toloka.assign_task(pool_id, ref_uuid)
                code: str = result.get('code', str())
                error_message: str = str()
                if code == 'CSRF_EXCEPTION':
                    result = await self._toloka.assign_task(pool_id, ref_uuid)
                    code = result.get('code', str())
                if code == 'CAPTCHA_REQUIRED':
                    payload: dict = result['payload']
                    url: str = payload['url']

                    print('Captcha URL:', url)
                    Notify()(subtitle='Waiting user input', message=title)
                    try:
                        key: str = payload['key']
                        timeout: int = payload['timeoutSeconds']
                        captcha: str = await asyncio.wait_for(self.input('Input captcha:'), timeout)
                        if captcha:
                            json: dict = await self._toloka.pass_captcha(key, captcha)
                            if json.get('success', False):
                                result = await self._toloka.assign_task(pool_id, ref_uuid)
                                code = result.get('code', str())
                            else:
                                error_message = 'Incorrect captcha'
                    except asyncio.TimeoutError:
                        error_message = 'Timeout of input captcha'
                if not code:
                    print(f'A task is activated: {title}')
                    Notify()(subtitle='The task is activated', message=title)
                    self._stats['activated_tasks'] += 1
                else:
                    if not error_message:
                        error_message = result.get('message', str())

                    string: str = f'Can\'t activate a task: {title}'
                    if error_message:
                        string += f'. {error_message}.'
                    print(string)
                    self._stats['activated_errors'] += 1

    async def __call__(self, *args, **kwargs) -> None:
        while True:
            if self._exit:
                break
            if self._pause == 2:
                await asyncio.sleep(1)
                continue
            try:
                toloka_tasks: list = await self._toloka.get_tasks()
                if toloka_tasks:
                    favorite_tasks: list = list(filter(
                        lambda t: t['projectMetaInfo'].get('bookmarked', False), toloka_tasks
                    ))
                    for task in favorite_tasks:
                        await self._assign_task(task)
                self._stats['requests'] += 1
                self._print_stats(len(toloka_tasks))
                if self._pause == 1:
                    print('Pause')
                    self._pause = 2
                    self._print_stats(len(toloka_tasks))
            except HttpError:
                self._stats['errors'] += 1
                await asyncio.sleep(1)
            except AccessDeniedError:
                print(colored('Access denied', 'red'))
                for i in range(60):
                    if self._exit:
                        break
                    await asyncio.sleep(1)
