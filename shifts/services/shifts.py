import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from shifts.models import Shift

__all__ = ('create_unconfirmed_shifts', 'confirm_shifts')


@dataclass(frozen=True, slots=True)
class ShiftDTO:
    id: int
    performer_telegram_id: int
    date: datetime.date


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
