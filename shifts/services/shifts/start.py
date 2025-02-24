from dataclasses import dataclass

from django.utils import timezone

from shifts.exceptions import ShiftNotFoundError
from shifts.models import Shift
from shifts.services.shifts import ensure_time_to_start_shift
from shifts.services.shifts.validators import (
    ensure_staff_has_no_active_shift,
    ensure_shift_confirmed,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftStartResult:
    id: int
    staff_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftStartInteractor:
    shift_id: int

    def execute(self) -> ShiftStartResult:
        ensure_time_to_start_shift()

        try:
            shift = Shift.objects.get(id=self.shift_id)
        except Shift.DoesNotExist:
            raise ShiftNotFoundError

        ensure_staff_has_no_active_shift(staff_id=shift.staff_id)
        ensure_shift_confirmed(shift)

        shift.started_at = timezone.now()
        shift.save(update_fields=('started_at',))

        return ShiftStartResult(
            id=shift.id,
            staff_id=shift.staff_id,
        )
