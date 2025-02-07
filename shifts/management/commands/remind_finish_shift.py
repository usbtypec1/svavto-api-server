import time

from django.core.management import BaseCommand

from shifts.selectors import get_staff_ids_with_active_shift
from telegram.services import get_telegram_bot, try_send_message


class Command(BaseCommand):
    help = ('Send notification to all staff who have not finished their shifts '
            'yet')

    def handle(self, *args, **options):
        bot = get_telegram_bot()
        staff_ids = get_staff_ids_with_active_shift()

        text = '❗️ Не забудьте завершить смену'
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
