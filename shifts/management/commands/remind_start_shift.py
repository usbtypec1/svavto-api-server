import time

from django.core.management import BaseCommand

from shifts.services.shifts import (
    get_staff_ids_with_not_started_shifts_for_today
)
from telegram.services import get_telegram_bot, try_send_message


class Command(BaseCommand):
    help = (
        'Send notification to all staff who have not start their shifts and'
        ' have not rejected their shifts yet'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--extra-warn',
            action='store_true',
            default=False,
            help='Send extra warning message',
        )

    def handle(self, *args, **options):
        bot = get_telegram_bot()
        extra_warn: bool = options['extra_warn']

        staff_ids = get_staff_ids_with_not_started_shifts_for_today()

        if extra_warn:
            text = ('❗️ Для корректного подсчета внесенных вами данных '
                    'начните смену до 23:59')
        else:
            text = '❗ Не забудьте начать смену на сегодня'

        for staff_id in staff_ids:
            is_sent = try_send_message(
                bot=bot,
                chat_id=staff_id,
                text=text,
            )
            if is_sent:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Message has been sent to staff {staff_id}',
                    )
                )
            else:
                self.stderr.write(
                    self.style.ERROR(
                        f'Message has not been sent to staff {staff_id}',
                    )
                )
            time.sleep(0.1)
