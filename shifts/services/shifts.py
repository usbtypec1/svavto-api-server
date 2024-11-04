import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from django.utils import timezone

from shifts.exceptions import (
    ShiftAlreadyConfirmedError,
    ShiftAlreadyFinishedError,
    ShiftByDateNotFoundError,
    ShiftNotConfirmedError,
    StaffHasActiveShiftError,
)
from shifts.models import Shift
from shifts.selectors import has_any_finished_shift

__all__ = (
    'create_unconfirmed_shifts',
    'confirm_shift',
    'start_shift',
    'ensure_staff_has_no_active_shift',
    'finish_shift',
    'get_shifts_by_staff_id',
)

from staff.models import Staff


@dataclass(frozen=True, slots=True)
class ShiftDTO:
    id: int
    performer_telegram_id: int
    date: datetime.date


def create_unconfirmed_shifts(
        *,
        staff: Staff,
        dates: Iterable[datetime.date],
) -> None:
    shifts = [Shift(staff=staff, date=date) for date in dates]
    Shift.objects.bulk_create(shifts)


def confirm_shift(
        *,
        date: datetime.date,
        staff_id: int,
) -> None:
    try:
        shift = Shift.objects.get(date=date, staff_id=staff_id)
    except Shift.DoesNotExist:
        raise ShiftByDateNotFoundError

    if shift.is_confirmed:
        raise ShiftAlreadyConfirmedError

    shift.confirmed_at = timezone.now()
    shift.save(update_fields=('confirmed_at',))


def start_shift(
        *,
        shift_id: int,
        car_wash_id: int,
) -> Shift:
    try:
        shift = (
            Shift.objects
            .select_related('car_wash', 'staff')
            .only('id', 'date', 'car_wash', 'staff')
            .get(id=shift_id)
        )
    except Shift.DoesNotExist:
        raise ShiftByDateNotFoundError

    if not shift.is_confirmed:
        raise ShiftNotConfirmedError

    if shift.is_started:
        raise StaffHasActiveShiftError

    shift.started_at = timezone.now()
    shift.car_wash_id = car_wash_id
    shift.save(update_fields=('started_at', 'car_wash_id'))

    return shift


def ensure_staff_has_no_active_shift(
        staff_id: int,
) -> None:
    if Shift.objects.filter(
            staff_id=staff_id,
            finished_at__isnull=True,
    ).exists():
        raise StaffHasActiveShiftError


def finish_shift(shift: Shift) -> dict:
    if shift.finished_at is not None:
        raise ShiftAlreadyFinishedError

    is_first_shift = not has_any_finished_shift(shift.staff_id)

    shift.finished_at = timezone.now()
    shift.save(update_fields=('finished_at',))

    return {
        'is_first_shift': is_first_shift,
        'staff_full_name': shift.staff.full_name,
        'car_numbers': shift.cartowash_set.values_list('number', flat=True),
    }


def get_shifts_by_staff_id(
        *,
        staff_id: int,
        month: int,
        year: int,
) -> list:
    return (
        Shift.objects
        .select_related('car_wash')
        .filter(
            staff_id=staff_id,
            date__month=month,
            date__year=year,
        )
    )
