import datetime
from dataclasses import dataclass

from shifts.exceptions import ShiftNotFoundError
from shifts.models import Shift


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftsDeleteOnStaffBanInteractor:
    """
    Interactor to delete shifts of staff if he gets banned.
    """
    staff_id: int
    from_date: datetime.date

    def execute(self) -> None:
        (
            Shift.objects
            .filter(staff_id=self.staff_id, date__gte=self.from_date)
            .delete()
        )


@dataclass(frozen=True, slots=True)
class ShiftDeleteByIdInteractor:
    """
    Delete shift by its ID.
    """
    shift_id: int

    def execute(self) -> None:
        deleted_count, _ = Shift.objects.filter(id=self.shift_id).delete()
        if deleted_count == 0:
            raise ShiftNotFoundError
