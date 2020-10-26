import sys
import asyncio
from collections.abc import Callable
from termcolor import colored
from pytoloka import Toloka
from pytoloka.exceptions import HttpError, AccessDeniedError
from notify import Notify


class Assigner:
    def __init__(self, toloka: Toloka) -> None:
        self._toloka: Toloka = toloka
        self._exit: bool = False
        self._pause: int = 0

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

    async def __call__(self, user_input: Callable[[str], []], *args, **kwargs) -> None:
        requests: int = 0
        errors: int = 0
        activated_tasks: int = 0
        activated_errors: int = 0
        while True:
            if self._exit:
                break
            if self._pause == 2:
                await asyncio.sleep(1)
                continue
            try:
                toloka_tasks: list = await self._toloka.get_tasks()
                for task in toloka_tasks:
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
                            if code == 'CSRF_EXCEPTION':
                                result = await self._toloka.assign_task(pool_id, ref_uuid)
                                code = result.get('code', str())
                            if code == 'CAPTCHA_REQUIRED':
                                payload: dict = result['payload']
                                key: str = payload['key']
                                url: str = payload['url']

                                print('Captcha URL:', url)
                                Notify()(subtitle='Waiting user input', message=title)
                                captcha: str = user_input('Input captcha:')
                                if captcha:
                                    json: dict = await self._toloka.pass_captcha(key, captcha)
                                    if json.get('success', False):
                                        result = await self._toloka.assign_task(pool_id, ref_uuid)
                                        code = result.get('code', str())
                            if not code:
                                print(f'A task is activated: {title}')
                                Notify()(subtitle='The task is activated', message=title)
                                activated_tasks += 1
                            else:
                                message = result.get('message')
                                print(f'Can\'t activate a task: {title}. {message}.')
                                activated_errors += 1
                requests += 1
                print('Requests: {}|{}. Activated tasks: {}|{}. Total tasks: {}.'.format(
                    colored(str(requests), 'green'), colored(str(errors), 'red'),
                    colored(str(activated_tasks), 'green'), colored(str(activated_errors), 'red'),
                    len(toloka_tasks)
                ))
                sys.stdout.write('\033[F')
                sys.stdout.write('\033[K')
                if self._pause == 1:
                    print('Pause')
                    self._pause = 2
            except HttpError:
                errors += 1
                await asyncio.sleep(1)
            except AccessDeniedError:
                print(colored('Access denied', 'red'))
                for i in range(60):
                    if self._exit:
                        break
                    await asyncio.sleep(1)
