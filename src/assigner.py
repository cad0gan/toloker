import sys
import asyncio
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
        count = 0
        while True:
            if self._exit:
                break
            if self._pause == 2:
                await asyncio.sleep(1)
                continue

            try:
                toloka_tasks = await self._toloka.get_tasks()
                print(f'Requests: {count + 1}. Total tasks: {len(toloka_tasks)}.')
                sys.stdout.write('\033[F')
                sys.stdout.write('\033[K')
                for task in toloka_tasks:
                    title = task['title']

                    if task['projectMetaInfo'].get('bookmarked'):
                        # if task['pools'][0].get('activeAssignments'):
                        #     print('Active task: {}'.format(title))
                        if not task['pools'][0].get('activeAssignments'):
                            pool_id = task['pools'][0]['id']
                            ref_uuid = task['refUuid']

                            print(f'Activating the task: {title}')
                            result = await self._toloka.assign_task(pool_id, ref_uuid)
                            code = result.get('code')
                            if code and code == 'CSRF_EXCEPTION':
                                result = await self._toloka.assign_task(pool_id, ref_uuid)
                                code = result.get('code')
                            if not code:
                                print(f'A task is activated: {title}')
                                Notify()(subtitle='The task was activated', message=title)
                            else:
                                message = result.get('message')
                                print(f'Can\'t activate a task: {title}. {message}.')
                if self._pause == 1:
                    print('Pause')
                    self._pause = 2
                count += 1
            except HttpError:
                await asyncio.sleep(1)
