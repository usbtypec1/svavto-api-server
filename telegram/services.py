from collections.abc import Iterable

from django.conf import settings
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InputMediaPhoto


__all__ = (
    'get_telegram_bot',
    'try_send_message',
    'try_send_photos_media_group',
    'try_get_chat_username',
    'get_dry_cleaning_telegram_bot',
)


def get_telegram_bot() -> TeleBot:
    return TeleBot(token=settings.TELEGRAM_BOT_TOKEN)


def get_dry_cleaning_telegram_bot() -> TeleBot:
    return TeleBot(token=settings.DRY_CLEANING_TELEGRAM_BOT_TOKEN)


def try_send_message(
        bot: TeleBot,
        chat_id: int,
        text: str,
        parse_mode: str | None = 'html',
        reply_markup: InlineKeyboardMarkup | None = None
) -> bool:
    for _ in range(5):
        try:
            return bool(
                bot.send_message(
                    chat_id,
                    text,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                ),
            )
        except Exception:
            pass
    else:
        return False


def try_send_photos_media_group(
        bot: TeleBot,
        chat_id: int,
        file_ids: Iterable[str],
        caption: str | None,
        parse_mode: str | None = 'html',
) -> bool:
    media = []
    file_ids = tuple(file_ids)

    if not file_ids:
        return False

    if caption is not None:
        file_id, *file_ids = file_ids
        media.append(
            InputMediaPhoto(
                media=file_id,
                caption=caption,
                parse_mode=parse_mode,
            ),
        )
    media += [InputMediaPhoto(media=file_id) for file_id in file_ids]

    for _ in range(5):
        try:
            bot.send_media_group(
                chat_id=chat_id,
                media=media,
            )
        except Exception as error:
            print(error)
            return False
        return True
    else:
        return False


def try_get_chat_username(
        bot: TeleBot,
        chat_id: int,
) -> str | None:
    for _ in range(5):
        try:
            chat = bot.get_chat(chat_id)
            return chat.username
        except Exception:
            return None
    else:
        return None
