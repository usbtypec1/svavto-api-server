from typing import TypedDict, TypeAlias

from celery.utils.log import get_task_logger

from django.utils import timezone
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from celery import shared_task

from mailing.services import create_telegram_bot
from staff.models import Staff

logger = get_task_logger(__name__)


class Button(TypedDict):
    text: str
    url: str


ButtonsRow: TypeAlias = list[Button]
ButtonsRows: TypeAlias = list[ButtonsRow]


def send_to_chats(
        *,
        bot: TeleBot,
        text: str,
        chat_ids: list[int],
        buttons_rows: ButtonsRows | None = None,
):
    markup = None if buttons_rows is None else build_reply_markup(buttons_rows)
    for chat_id in chat_ids:
        try:
            bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=markup,
            )
        except ApiTelegramException as error:
            logger.warning(
                f'Could not send message to {chat_id}: {str(error)}'
            )


def build_reply_markup(buttons_rows: ButtonsRows) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        keyboard=[
            [
                InlineKeyboardButton(
                    text=button['text'],
                    url=button['url']
                ) for button in buttons_row
            ] for buttons_row in buttons_rows
        ]
    )


@shared_task
def start_mailing_to_staff_with_latest_activity(
        text: str,
        last_days: int,
):
    now = timezone.now() - timezone.timedelta(days=last_days)
    bot = create_telegram_bot()
    staff_ids = (
        Staff.objects
        .filter(last_activity_at__gte=now)
        .values_list('id', flat=True)
    )
    send_to_chats(
        bot=bot,
        text=text,
        chat_ids=staff_ids,
    )


@shared_task
def start_mailing_all_staff(text: str, buttons_rows: ButtonsRows | None = None):
    bot = create_telegram_bot()
    staff_ids = Staff.objects.values_list('id', flat=True)
    send_to_chats(
        bot=bot,
        text=text,
        chat_ids=staff_ids,
        buttons_rows=buttons_rows,
    )


@shared_task
def start_mailing_for_specific_staff(
        text: str,
        chat_ids: list[int],
        buttons_rows: ButtonsRows | None = None,
):
    bot = create_telegram_bot()
    send_to_chats(
        bot=bot,
        text=text,
        chat_ids=chat_ids,
        buttons_rows=buttons_rows,
    )
