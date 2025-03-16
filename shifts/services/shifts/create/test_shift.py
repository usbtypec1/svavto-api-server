import datetime
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from shifts.models import Shift
from staff.models import Staff


@dataclass(frozen=True, slots=True)
class ShiftTestCreateResult:
    staff_id: int
    staff_full_name: str
    shift_id: int
    shift_date: datetime.date


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftTestCreateInteractor:
    """
    Create test shift for staff for specific date or refresh test shift.

    Args:
        staff: staff ORM object.
        date: date of test shift.

    """

    staff: Staff
    date: datetime.date

    @transaction.atomic
    def execute(self) -> ShiftTestCreateResult:
        Shift.objects.filter(staff_id=self.staff.id, is_test=True).delete()
        shift = Shift(
            staff_id=self.staff.id,
            date=self.date,
            confirmed_at=timezone.now(),
            is_test=True,
        )
        shift.full_clean()
        shift.save()
        return ShiftTestCreateResult(
            staff_id=self.staff.id,
            staff_full_name=self.staff.full_name,
            shift_id=shift.id,
            shift_date=shift.date,
        )
