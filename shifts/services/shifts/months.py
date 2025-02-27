from dataclasses import dataclass

from django.db.models.functions import TruncMonth
from django.utils import timezone

from shifts.models import Shift


@dataclass(frozen=True, slots=True, kw_only=True)
class MonthAndYear:
    month: int
    year: int


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffShiftsMonths:
    staff_id: int
    months: list[MonthAndYear]


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffShiftsMonthListInteractor:
    staff_id: int

    def execute(self) -> StaffShiftsMonths:
        now = timezone.localdate()
        months = (
            Shift.objects.filter(
                staff_id=self.staff_id,
                date__gte=now,
            )
            .annotate(month_year=TruncMonth('date'))
            .values('month_year')
            .distinct()
            .order_by('month_year')
        )
        return StaffShiftsMonths(
            staff_id=self.staff_id,
            months=[
                MonthAndYear(
                    month=month['month_year'].month,
                    year=month['month_year'].year,
                )
                for month in months
            ],
        )
