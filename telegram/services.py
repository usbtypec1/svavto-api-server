from django.conf import settings
from telebot import TeleBot

__all__ = ('get_telegram_bot', 'try_send_message')


def get_telegram_bot() -> TeleBot:
    return TeleBot(token=settings.TELEGRAM_BOT_TOKEN)


def try_send_message(
        bot: TeleBot,
        chat_id: int,
        text: str,
) -> bool:
    try:
        bot.send_message(chat_id, text)
    except Exception:
        return False

