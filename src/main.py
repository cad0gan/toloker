import asyncio
from pytoloka import Toloka
from config import Config
from auto_accept import AutoAccept


if __name__ == '__main__':
    config = Config()
    toloka = Toloka()
    if asyncio.run(toloka.login(config.username, config.password)):
        asyncio.run(AutoAccept(toloka)())
