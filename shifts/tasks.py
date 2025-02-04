import time

from celery import shared_task

from shifts.selectors import get_staff_ids_with_active_shift
from telegram.services import get_telegram_bot, try_send_message


@shared_task
def remind_finish_shift() -> None:
    """
    Send notification to all staff who have not finished their shifts yet.
    """
    bot = get_telegram_bot()
    staff_ids = get_staff_ids_with_active_shift()

    text = '❗️ Не забудьте завершить смену'
    for staff_id in staff_ids:
        try_send_message(
            bot=bot,
            chat_id=staff_id,
            text=text,
        )
        time.sleep(0.1)
