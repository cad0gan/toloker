import subprocess
from config import Config
from singleton import Singleton
from telegram_bot import TelegramBot


class Notify(metaclass=Singleton):
    def __init__(self):
        config = Config()
        self._notify = config.notify

    @staticmethod
    def _terminal_notifier(title: str, subtitle: str, message: str):
        title = f'-title "{title}"'
        subtitle = f'-subtitle "{subtitle}"'
        message = f'-message "{message}"'
        cmd = f'terminal-notifier {title} {subtitle} {message} -sound default'
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
