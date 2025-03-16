from collections.abc import Iterable
from dataclasses import dataclass

from django.db.models import Count, Q

from shifts.exceptions import MonthNotAvailableError
from shifts.models import AvailableDate
from staff.models import Staff


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffIdAndName:
    id: int
    full_name: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DeadSoulsForMonth:
    month: int
    year: int
    staff_list: list[StaffIdAndName]


def map_dict_to_staff_id_and_name(
    staff_list: Iterable[dict],
) -> list[StaffIdAndName]:
    return [
        StaffIdAndName(id=staff["id"], full_name=staff["full_name"])
        for staff in staff_list
    ]


def ensure_month_is_available(*, month: int, year: int) -> None:
    if not AvailableDate.objects.filter(month=month, year=year).exists():
        raise MonthNotAvailableError(month=month, year=year)


def get_staff_with_one_test_shift(
    *,
    year: int,
    month: int,
) -> list[StaffIdAndName]:
    staff_list = (
        Staff.objects.filter(
            banned_at__isnull=True,
            shift__date__year=year,
            shift__date__month=month,
        )
        .annotate(
            test_shift_count=Count("shift", filter=Q(shift__is_test=True)),
            all_shift_count=Count("shift"),
        )
        .filter(
            test_shift_count=1,
            all_shift_count=1,
        )
        .values("id", "full_name")
    )
    return map_dict_to_staff_id_and_name(staff_list)


def get_staff_with_no_shifts(
    *,
    year: int,
    month: int,
) -> list[StaffIdAndName]:
    staff_list = (
        Staff.objects.filter(banned_at__isnull=True)
        .exclude(
            shift__date__year=year,
            shift__date__month=month,
        )
        .distinct("id")
        .values("id", "full_name")
    )
    return map_dict_to_staff_id_and_name(staff_list)


@dataclass(frozen=True, slots=True, kw_only=True)
class DeadSoulsReadInteractor:
    month: int
    year: int

    def execute(self):
        ensure_month_is_available(month=self.month, year=self.year)

        staff_list = {
            *get_staff_with_no_shifts(month=self.month, year=self.year),
            *get_staff_with_one_test_shift(month=self.month, year=self.year),
        }

        return DeadSoulsForMonth(
            month=self.month,
            year=self.year,
            staff_list=list(staff_list),
        )
