from functools import lru_cache
import logging

from telebot import TeleBot
from django.conf import settings

from telebot.apihelper import ApiTelegramException

__all__ = ('create_telegram_bot', 'try_send_message')

logger = logging.getLogger('mailing')


@lru_cache
def create_telegram_bot() -> TeleBot:
    return TeleBot(settings.TELEGRAM_BOT_TOKEN)


def try_send_message(
        chat_id: int,
        text: str,
) -> bool:
    bot = create_telegram_bot()
    try:
        bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode='html',
        )
    except ApiTelegramException as error:
        message = f'Could not send message to {chat_id}: {str(error)}'
        logger.warning(message)
        return False
    return True
