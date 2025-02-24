import datetime

from django.utils import timezone


__all__ = ('get_current_shift_date',)


def get_current_shift_date() -> datetime.date:
    """
    The **shift date** is the date when the shift was scheduled to start.
    Since the shift begins at 10 PM and ends at 7 AM,
    it technically spans two calendar days.
    However, the shift date is considered to be the date of its starting
    moment.

    Returns:
        The date of the shift.
    """
    now = timezone.localtime()
    if now.hour <= 20:
        previous_day = now - datetime.timedelta(days=1)
        return previous_day.date()
    return now.date()
