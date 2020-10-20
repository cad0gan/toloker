import sys
import asyncio
from termcolor import colored
from pytoloka import Toloka
from pytoloka.exceptions import HttpError
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
            self._pause = 1
        elif self._pause == 2:
            print('Unpause')
            self._pause = False

    async def __call__(self, *args, **kwargs) -> None:
        count: int = 0
        errors: int = 0
        while True:
            if self._exit:
                break
            if self._pause == 2:
                await asyncio.sleep(1)
                continue

            try:
                toloka_tasks: list = await self._toloka.get_tasks()
                print('Requests: {}|{}. Total tasks: {}.'.format(
                    colored(str(count + 1), 'green'), colored(str(errors), 'red'),
                    len(toloka_tasks)
                ))
                sys.stdout.write('\033[F')
                sys.stdout.write('\033[K')
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
                            code: str = result.get('code')
                            if code and code == 'CSRF_EXCEPTION':
                                result = await self._toloka.assign_task(pool_id, ref_uuid)
                                code = result.get('code')
                            if not code:
                                print(f'A task is activated: {title}')
                                Notify()(subtitle='The task is activated', message=title)
                            else:
                                message = result.get('message')
                                print(f'Can\'t activate a task: {title}. {message}.')
                if self._pause == 1:
                    print('Pause')
                    self._pause = 2
                count += 1
            except HttpError:
                errors += 1
                await asyncio.sleep(1)
