import time
from collections.abc import Iterable

from celery import shared_task

from core.services import get_current_shift_date, to_moscow_timezone
from shifts.models import Shift
from staff.selectors import get_admin_ids
from telegram.services import (
    get_telegram_bot,
    try_send_message,
)


def format_started_shifts(shifts: Iterable[Shift]) -> str:
    lines: list[str] = [f'Список подтвердивших смену на сегодня:']
    for shift in shifts:
        lines.append(
            f'📍 {shift.staff.full_name}'
            f' - в {to_moscow_timezone(shift.started_at):%H:%M}'
        )
    return '\n'.join(lines)


def format_not_started_shifts(shifts: Iterable[Shift]):
    lines: list[str] = [
        f'Список не подтвердивших смену на сегодня:'
    ]
    for shift in shifts:
        lines.append(f'📍 {shift.staff.full_name}')
    return '\n'.join(lines)


@shared_task
def send_today_shifts_report():
    shift_date = get_current_shift_date()
    bot = get_telegram_bot()

    admin_staff_ids = get_admin_ids()

    shifts = (
        Shift.objects
        .filter(date=shift_date)
        .only('staff__full_name', 'started_at')
    )

    started_shifts = [shift for shift in shifts if shift.is_started]
    not_started_shifts = [shift for shift in shifts if not shift.is_started]

    text_messages: list[str] = []

    if started_shifts:
        text_messages.append(format_started_shifts(started_shifts))

    if not_started_shifts:
        text_messages.append(format_not_started_shifts(not_started_shifts))

    for admin_staff_id in admin_staff_ids:
        for text in text_messages:
            try_send_message(bot=bot, chat_id=admin_staff_id, text=text)
            time.sleep(1)
