from collections.abc import Iterable
import datetime

from shifts.models import Shift
from shifts.selectors import ShiftDTO

__all__ = ('create_unconfirmed_shifts', 'confirm_shifts')


def create_unconfirmed_shifts(
        performer_id: int,
        dates: Iterable[datetime.date],
) -> list[ShiftDTO]:
    shifts = [
        Shift(performer_id=performer_id, date=date)
        for date in dates
    ]
    shifts = Shift.objects.bulk_create(shifts)
    return [
        ShiftDTO(
            id=shift.id,
            performer_telegram_id=shift.performer_id,
            date=shift.date,
        )
        for shift in shifts
    ]


def confirm_shifts(shift_ids: Iterable[int]):
    Shift.objects.filter(id__in=shift_ids).update(is_confirmed=True)
