from dataclasses import dataclass

from django.utils import timezone

from shifts.exceptions import ShiftAlreadyConfirmedError, ShiftNotFoundError
from shifts.models import Shift


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftConfirmResult:
    shift_id: int
    staff_id: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftConfirmInteractor:
    shift_id: int

    def execute(self) -> ShiftConfirmResult:
        try:
            shift = Shift.objects.get(id=self.shift_id)
        except Shift.DoesNotExist:
            raise ShiftNotFoundError

        if shift.confirmed_at is not None:
            raise ShiftAlreadyConfirmedError

        shift.confirmed_at = timezone.now()
        shift.save(update_fields=("confirmed_at",))

        return ShiftConfirmResult(
            shift_id=shift.id,
            staff_id=shift.staff_id,
        )
