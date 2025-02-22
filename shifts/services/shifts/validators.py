from shifts.exceptions import ShiftNotFoundError, StaffHasActiveShiftError
from shifts.models import Shift


def ensure_staff_has_no_active_shift(staff_id: int) -> None:
    if Shift.objects.filter(
            staff_id=staff_id,
            started_at__isnull=False,
            finished_at__isnull=True,
    ).exists():
        raise StaffHasActiveShiftError


def ensure_shift_exists(shift_id: int) -> None:
    if not Shift.objects.filter(id=shift_id).exists():
        raise ShiftNotFoundError
