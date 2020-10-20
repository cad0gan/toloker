import asyncio
from config import Config
from singleton import Singleton
from telegram.ext import Updater, CommandHandler


class TelegramBot(metaclass=Singleton):
    def __init__(self) -> None:
        self._updater: Updater = Updater(Config().telegram_token)
        self._exit: bool = False

    def exit(self) -> None:
        if not self._exit:
            self._exit = True

    @staticmethod
    def _handle_start(update, context) -> None:
        update.message.reply_text(str(update.message.chat_id))

    def send_message(self, message: str) -> None:
        self._updater.bot.send_message(Config().telegram_chat_id, message)

    async def __call__(self, *args, **kwargs) -> None:
        dp = self._updater.dispatcher
        dp.add_handler(CommandHandler('start', self._handle_start))
        while True:
            if self._exit:
                self._updater.stop()
                return
            self._updater.start_polling()
            await asyncio.sleep(1)
