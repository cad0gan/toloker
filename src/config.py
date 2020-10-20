import yaml
from pathlib import Path
from singleton import Singleton


class Config(metaclass=Singleton):
    def __init__(self) -> None:
        directory = Path.home().joinpath('.config', 'toloker')
        directory.mkdir(exist_ok=True)
        path = directory.joinpath('config.yml')
        with open(path) as fp:
            self._config = yaml.safe_load(fp)

    @property
    def username(self) -> str:
        return self._config['username']

    @property
    def password(self) -> str:
        return self._config['password']

    @property
    def telegram_token(self) -> str:
        return self._config.get('telegram-token', str())

    @property
    def telegram_chat_id(self) -> int:
        return self._config.get('telegram-chat_id', int())

    @property
    def notify(self):
        return self._config.get('notify')
