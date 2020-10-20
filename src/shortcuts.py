import asyncio
from pytoloka import Toloka
from config import Config


def login(toloka: Toloka) -> bool:
    config: Config = Config()
    if asyncio.run(toloka.login(config.username, config.password)):
        return True
    else:
        print('You are not logged in!')
        return False
