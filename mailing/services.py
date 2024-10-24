from telebot import TeleBot
from django.conf import settings

__all__ = ('create_telegram_bot',)


def create_telegram_bot() -> TeleBot:
    return TeleBot(settings.TELEGRAM_BOT_TOKEN)
