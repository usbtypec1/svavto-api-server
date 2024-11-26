from collections.abc import Iterable

from django.conf import settings
from telebot import TeleBot
from telebot.types import InputMediaPhoto

__all__ = (
    'get_telegram_bot',
    'try_send_message',
    'try_send_photos_media_group',
)


def get_telegram_bot() -> TeleBot:
    return TeleBot(token=settings.TELEGRAM_BOT_TOKEN)


def try_send_message(
    bot: TeleBot,
    chat_id: int,
    text: str,
) -> bool:
    for _ in range(5):
        try:
            bot.send_message(chat_id, text)
        except Exception:
            pass
        return True
    else:
        return False


def try_send_photos_media_group(
    bot: TeleBot,
    chat_id: int,
    file_ids: Iterable[str],
    caption: str | None,
) -> bool:
    media = []
    file_ids = tuple(file_ids)

    if not file_ids:
        return False

    if caption is not None:
        file_id, *file_ids = file_ids
        media.append(InputMediaPhoto(media=file_id, caption=caption))
    media += [InputMediaPhoto(media=file_id) for file_id in file_ids]

    for _ in range(5):
        try:
            bot.send_media_group(
                chat_id=chat_id,
                media=media,
            )
        except Exception as error:
            print(error)
        return True
    else:
        return False
