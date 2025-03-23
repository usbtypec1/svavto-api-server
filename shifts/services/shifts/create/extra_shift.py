import datetime
import functools
import operator
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypeAlias, TypedDict

from django.db.models import Q, QuerySet
from django.utils import timezone

from shifts.models import Shift, ShiftCarsThreshold
from staff.models import Staff


class StaffIdAndDateTypedDict(TypedDict):
    staff_id: int
    date: datetime.date


StaffIdAndDate: TypeAlias = tuple[int, datetime.date]


@dataclass(frozen=True, slots=True, kw_only=True)
class ConflictAndNonConflictShifts:
    conflict_shifts: list[StaffIdAndDateTypedDict]
    non_conflict_shifts: list[StaffIdAndDateTypedDict]


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatedExtraShift:
    id: int
    staff_id: int
    date: datetime.date
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ExtraShiftsCreateResult:
    missing_staff_ids: tuple[int, ...]
    created_shifts: list[CreatedExtraShift]
    conflict_shifts: list[StaffIdAndDateTypedDict]


def separate_conflict_non_test_shifts(
    shifts: Iterable[StaffIdAndDateTypedDict],
) -> ConflictAndNonConflictShifts:
    expected_shifts: set[StaffIdAndDate] = {
        (shift["staff_id"], shift["date"]) for shift in shifts
    }
    filters = functools.reduce(
        operator.or_,
        [Q(staff_id=staff_id, date=date) for staff_id, date in expected_shifts],
        Q(),
    )

    existing_shifts: QuerySet[Shift | dict] = Shift.objects.filter(
        filters, is_test=False
    ).values("staff_id", "date")
    existing_shifts: set[StaffIdAndDate] = {
        (shift["staff_id"], shift["date"]) for shift in existing_shifts
    }

    conflict_shifts = expected_shifts.intersection(existing_shifts)
    non_conflict_shifts = expected_shifts - conflict_shifts

    return ConflictAndNonConflictShifts(
        conflict_shifts=[
            {"staff_id": staff_id, "date": date} for staff_id, date in conflict_shifts
        ],
        non_conflict_shifts=[
            {"staff_id": staff_id, "date": date}
            for staff_id, date in non_conflict_shifts
        ],
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class MissingAndExistingStaffIds:
    missing_staff_ids: tuple[int, ...]
    existing_staff_ids: tuple[int, ...]


def separate_staff_by_existence(
    staff_ids: Iterable[int],
) -> MissingAndExistingStaffIds:
    staff_ids = set(staff_ids)
    existing_staff_ids = set(
        Staff.objects.filter(id__in=staff_ids).values_list("id", flat=True)
    )
    missing_staff_ids = tuple(staff_ids - existing_staff_ids)
    existing_staff_ids = tuple(existing_staff_ids)
    return MissingAndExistingStaffIds(
        missing_staff_ids=missing_staff_ids,
        existing_staff_ids=existing_staff_ids,
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftExtraCreateInteractor:
    shifts: list[StaffIdAndDateTypedDict]

    def get_shifts_of_staff(
        self,
        staff_ids: Iterable[int],
    ) -> list[StaffIdAndDateTypedDict]:
        staff_ids = set(staff_ids)
        return [shift for shift in self.shifts if shift["staff_id"] in staff_ids]

    def execute(self) -> ExtraShiftsCreateResult:
        staff_ids = [shift["staff_id"] for shift in self.shifts]
        separated_staff = separate_staff_by_existence(staff_ids)
        shifts_of_existing_staff = self.get_shifts_of_staff(
            separated_staff.existing_staff_ids,
        )
        separated_shifts = separate_conflict_non_test_shifts(
            shifts=shifts_of_existing_staff
        )
        transferred_cars_threshold = ShiftCarsThreshold.get()
        shifts_to_create = [
            Shift(
                staff_id=shift["staff_id"],
                date=shift["date"],
                is_extra=True,
                confirmed_at=timezone.now(),
                transferred_cars_threshold=transferred_cars_threshold,
            )
            for shift in separated_shifts.non_conflict_shifts
        ]
        created_shifts = Shift.objects.bulk_create(shifts_to_create)
        created_shifts = [
            CreatedExtraShift(
                id=shift.id,
                staff_id=shift.staff_id,
                date=shift.date,
                created_at=shift.created_at,
            )
            for shift in created_shifts
        ]
        return ExtraShiftsCreateResult(
            created_shifts=created_shifts,
            missing_staff_ids=separated_staff.missing_staff_ids,
            conflict_shifts=separated_shifts.conflict_shifts,
        )
