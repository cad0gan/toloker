import asyncio
import argparse
from pytoloka import Toloka
from config import Config
from auto_accept import AutoAccept


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs='*')
    args = parser.parse_args()

    if args.action == 'accept':
        config = Config()
        toloka = Toloka()
        if asyncio.run(toloka.login(config.username, config.password)):
            asyncio.run(AutoAccept(toloka)())
