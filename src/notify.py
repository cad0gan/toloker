import subprocess
from config import Config
from singleton import Singleton
from telegram_bot import TelegramBot


class Notify(metaclass=Singleton):
    def __init__(self) -> None:
        config: Config = Config()
        self._notify: list = config.notify

    @staticmethod
    def _terminal_notifier(title: str, subtitle: str, message: str):
        title: str = f'-title "{title}"'
        subtitle: str = f'-subtitle "{subtitle}"'
        message: str = f'-message "{message}"'
        cmd: str = f'terminal-notifier {title} {subtitle} {message} -sound default'
        subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @staticmethod
    def _telegram(message: str):
        TelegramBot().send_message(message)

    def __call__(self, title: str = 'toloker', subtitle: str = '', message: str = ''):
        if not message:
            raise AttributeError
        for notify in self._notify:
            if notify == 'terminal-notifier':
                self._terminal_notifier(title, subtitle, message)
            if notify == 'telegram':
                self._telegram(f'{subtitle}: {message}')
