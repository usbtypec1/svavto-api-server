import datetime

from celery import shared_task
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from shifts.selectors import (
    get_staff_ids_by_shift_date,
    get_staff_ids_by_shift_ids,
)

__all__ = ('send_staff_shift_confirmation',)


def build_shift_confirm_reply_markup(
        shift_id: int,
) -> InlineKeyboardMarkup:
    accept_button = InlineKeyboardButton(
        text='Подтвердить',
        callback_data=f'shift_confirm_accept:{shift_id}'
    )
    reject_button = InlineKeyboardButton(
        text='Отклонить',
        callback_data=f'shift_confirm_reject:{shift_id}',
    )
    return InlineKeyboardMarkup(keyboard=[[accept_button, reject_button]])


def format_shift_confirm_text(date: datetime.date) -> str:
    return (
        f'📆 Подтвердите выход на смену на выбранную дату {date:%d.%m.%Y}'
    )


@shared_task
def send_staff_shift_confirmation(
        staff_shift_ids: list[int] | None,
        date: datetime.date | None,
) -> None:
    if staff_shift_ids is None:
        shift_and_staff_ids = get_staff_ids_by_shift_date(date)
    else:
        shift_and_staff_ids = get_staff_ids_by_shift_ids(staff_shift_ids)

    text = format_shift_confirm_text(date)
    for shift_and_staff_id in shift_and_staff_ids:
        reply_markup = build_shift_confirm_reply_markup(
            shift_id=shift_and_staff_id.shift_id,
        )