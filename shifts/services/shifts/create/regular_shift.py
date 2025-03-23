import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from shifts.exceptions import ShiftAlreadyExistsError
from shifts.models import Shift, ShiftCarsThreshold
from staff.models import Staff


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftItem:
    id: int
    date: datetime.date


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftsCreateResult:
    staff_id: int
    staff_full_name: str
    shifts: list[ShiftItem]


def get_existing_shift_dates(
    *,
    staff_id: int,
    expected_dates: Iterable[datetime.date],
) -> set[datetime.date]:
    """
    Get existing shift dates from the database.

    Keyword Args:
        staff_id: staff id.
        expected_dates: existing shifts within these dates.

    Returns:
        set[datetime.date]: dates of existing shifts.
    """
    return set(
        Shift.objects.filter(
            staff_id=staff_id,
            date__in=expected_dates,
            is_test=False,
        ).values_list("date", flat=True)
    )


def validate_conflict_shift_dates(
    *,
    staff_id: int,
    expected_dates: Iterable[datetime.date],
) -> None:
    """
    Check if there are any conflicts with existing shifts.

    Keyword Args:
        staff_id: staff id.
        expected_dates: dates of shifts to be created.

    Raises:
        ShiftAlreadyExistsError: If shift already exists on any expected date.
    """
    existing_shift_dates = get_existing_shift_dates(
        staff_id=staff_id,
        expected_dates=expected_dates,
    )
    print(existing_shift_dates, set(expected_dates))
    conflict_dates = set(expected_dates).intersection(existing_shift_dates)
    if conflict_dates:
        raise ShiftAlreadyExistsError(conflict_dates=conflict_dates)


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftRegularCreateInteractor:
    """
    Create regular shifts for staff for specific dates.

    Args:
        staff: staff to create shifts for.
        dates: shift dates to create.
    """

    staff: Staff
    dates: Iterable[datetime.date]

    def execute(self) -> ShiftsCreateResult:
        """
        Raises:
            ShiftAlreadyExistsError: If shift already exists on any date.

        Returns:
            ShiftsCreateResult object.
        """
        validate_conflict_shift_dates(
            staff_id=self.staff.id,
            expected_dates=self.dates,
        )
        transferred_cars_threshold = ShiftCarsThreshold.get()
        shifts_to_create = [
            Shift(
                staff=self.staff,
                date=date,
                transferred_cars_threshold=transferred_cars_threshold,
            ) for date in self.dates]
        shifts = Shift.objects.bulk_create(shifts_to_create)

        shifts = [ShiftItem(id=shift.id, date=shift.date) for shift in shifts]
        return ShiftsCreateResult(
            staff_id=self.staff.id,
            staff_full_name=self.staff.full_name,
            shifts=shifts,
        )
