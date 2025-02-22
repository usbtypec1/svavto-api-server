from django.utils import timezone

from shifts.exceptions import ShiftNotFoundError, StaffHasActiveShiftError
from shifts.models import Shift


def start_shift(
        *,
        shift_id: int,
        car_wash_id: int,
) -> Shift:
    try:
        shift = (
            Shift.objects.select_related('car_wash', 'staff')
            .only('id', 'date', 'car_wash', 'staff')
            .get(id=shift_id)
        )
    except Shift.DoesNotExist:
        raise ShiftNotFoundError

    if shift.is_started:
        raise StaffHasActiveShiftError

    shift.started_at = timezone.now()
    shift.car_wash_id = car_wash_id
    shift.save(update_fields=('started_at', 'car_wash_id'))

    return shift
