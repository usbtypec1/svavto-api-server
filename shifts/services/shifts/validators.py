import datetime

from django.utils import timezone

from core.services import get_current_shift_date
from shifts.exceptions import (
    InvalidTimeToStartShiftError, ShiftAlreadyFinishedError,
    ShiftNotConfirmedError, ShiftNotFoundError,
    StaffHasActiveShiftError,
)
from shifts.models import Shift


def ensure_staff_has_no_active_shift(staff_id: int) -> None:
    if Shift.objects.filter(
            staff_id=staff_id,
            started_at__isnull=False,
            finished_at__isnull=True,
    ).exists():
        raise StaffHasActiveShiftError


def ensure_shift_not_finished(shift: Shift) -> None:
    if shift.finished_at is not None:
        raise ShiftAlreadyFinishedError(shift_date=shift.date)


def ensure_shift_exists(shift_id: int) -> None:
    if not Shift.objects.filter(id=shift_id).exists():
        raise ShiftNotFoundError


def ensure_shift_confirmed(shift: Shift) -> None:
    if shift.confirmed_at is None:
        raise ShiftNotConfirmedError


def ensure_time_to_start_shift() -> None:
    now = timezone.now()

    shift_date = get_current_shift_date()
    start_time = datetime.datetime.combine(
        shift_date,
        datetime.time(18, 30),
        tzinfo=datetime.UTC,
    )
    next_day = start_time + datetime.timedelta(days=1)
    next_day_noon = next_day.replace(
        hour=9,
        minute=0,
        second=0,
        microsecond=0,
    )
    if not (start_time <= now <= next_day_noon):
        raise InvalidTimeToStartShiftError
