import sys
import asyncio
from pytoloka import Toloka
from pytoloka.exceptions import HttpError
from notify import Notify


class AutoAccept:
    def __init__(self, toloka: Toloka) -> None:
        self._toloka: Toloka = toloka
        self._exit: bool = False

    def exit(self) -> None:
        if not self._exit:
            print('Exiting...')
            self._exit = True

    async def __call__(self, *args, **kwargs) -> None:
        count = 0
        while True:
            if self._exit:
                break
            try:
                toloka_tasks = await self._toloka.get_tasks()
                count += 1
                print(f'Requests: {count}')
                sys.stdout.write('\033[F')
                sys.stdout.write('\033[K')
                for task in toloka_tasks:
                    title = task['title']

                    if task['projectMetaInfo'].get('bookmarked'):
                        # if task['pools'][0].get('activeAssignments'):
                        #     print('Active task: {}'.format(title))
                        if not task['pools'][0].get('activeAssignments'):
                            pool_id = task['pools'][0]['id']

                            print(f'Activating the task: {title}')
                            result = await self._toloka.assign_task(pool_id, task['refUuid'])
                            if not result.get('id'):
                                result = await self._toloka.assign_task(pool_id, task['refUuid'])
                            if result.get('id'):
                                print(f'A task was activated: {title}')
                                Notify()(subtitle='The task was activated', message=title)
                            else:
                                print(f'Can\'t activate a task: {title}')
            except HttpError:
                await asyncio.sleep(1)
