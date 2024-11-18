from datetime import datetime, timedelta
from turtledemo.penrose import start

from celery import shared_task
from django.utils import timezone

from shifts.models import Shift
from staff.models import AdminStaff
from telegram.services import get_telegram_bot, try_send_message


def to_moscow_time(date: datetime):
    return date + timedelta(hours=3)


@shared_task
def send_today_shifts_report():
    now = to_moscow_time(timezone.now())
    bot = get_telegram_bot()

    shifts = Shift.objects.select_related('staff').filter(date=now.date())

    admin_staff_ids = AdminStaff.objects.values_list('id', flat=True)

    started_shifts = [shift for shift in shifts if shift.is_started]
    not_started_shifts = [shift for shift in shifts if not shift.is_started]

    if started_shifts:
        started_shifts_staff = [
            (
                f'📍 {shift.staff.full_name}'
                f' - в {to_moscow_time(shift.started_at):H:M}'
            )
            for shift in started_shifts
        ]
        started_shifts_message_lines: list[str] = [
            f'Список подтвердивших смену на сегодня:'
        ]
        started_shifts_message_lines += started_shifts_staff
        started_shifts_message = '\n'.join(started_shifts_message_lines)

        for admin_staff_id in admin_staff_ids:
            try_send_message(
                bot=bot,
                chat_id=admin_staff_id,
                text=started_shifts_message,
            )

    if not_started_shifts:
        not_started_shifts_staff = [
            f'📍 {shift.staff.full_name}' for shift in not_started_shifts
        ]
        not_started_shifts_message_lines: list[str] = [
            f'Список не подтвердивших смену на сегодня:'
        ]
        not_started_shifts_message_lines += not_started_shifts_staff
        not_started_shifts_message = '\n'.join(not_started_shifts_message_lines)

        for admin_staff_id in admin_staff_ids:
            try_send_message(
                bot=bot,
                chat_id=admin_staff_id,
                text=not_started_shifts_message,
            )
