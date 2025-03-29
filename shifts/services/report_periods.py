import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

import pendulum

from shifts.models import Shift
from staff.selectors import ensure_staff_exists


__all__ = (
    "Period",
    "get_report_periods_of_dates",
    "get_shift_dates_of_staff",
    "StaffReportPeriods",
    "StaffReportPeriodsReadInteractor",
    'get_report_period_by_number',
    "ReportPeriod",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class Period:
    from_date: pendulum.Date
    to_date: pendulum.Date

    def __contains__(self, date: pendulum.Date) -> bool:
        return self.from_date <= date <= self.to_date

    def __lt__(self, other: "Period") -> bool:
        """
        Defines sorting behavior for Period objects.
        Periods are sorted by their start date (from_date).
        """
        return self.from_date < other.from_date


@dataclass(frozen=True, slots=True, kw_only=True)
class ReportPeriod(Period):
    month: int
    year: int
    number: int

    @classmethod
    def from_number(cls, year: int, month: int, number: int) -> Self:
        """
        Creates a ReportPeriod instance from year, month, and period number.
        """
        return get_report_period_by_number(
            year=year,
            month=month,
            report_period_number=number,
        )

    def next(self) -> Self:
        """
        Returns the next ReportPeriod instance.
        """
        if self.number == 1:
            return ReportPeriod.from_number(
                year=self.year,
                month=self.month,
                number=2,
            )
        next_month = pendulum.date(self.year, self.month, 1).add(months=1)
        return ReportPeriod.from_number(
            year=next_month.year,
            month=next_month.month,
            number=1,
        )

    def __le__(self, other: Self) -> bool:
        """
        Defines less than or equal to behavior for ReportPeriod objects.
        """
        return self.from_date <= other.from_date



@dataclass(frozen=True, slots=True, kw_only=True)
class StaffReportPeriods:
    staff_id: int
    periods: list[Period]


def get_report_periods_of_dates(
        dates: Iterable[datetime.date],
) -> list[ReportPeriod]:
    """
    Generates an array of unique periods that at least one date belongs to.

    Args:
        dates (list[datetime.date]): Array of dates.

    Returns:
        list[Period]: Array of unique periods covering at least one date.
    """
    periods: set[ReportPeriod] = set()

    dates = [pendulum.instance(date) for date in dates]

    for date in dates:
        is_first_half_of_month = date.day <= 15
        if is_first_half_of_month:
            period = ReportPeriod(
                from_date=pendulum.date(date.year, date.month, 1),
                to_date=pendulum.date(date.year, date.month, 15),
                month=date.month,
                year=date.year,
                number=1,
            )
        else:
            next_month = date.add(months=1)
            last_day = next_month.start_of("month").subtract(days=1)
            period = ReportPeriod(
                from_date=pendulum.date(date.year, date.month, 16),
                to_date=last_day,
                month=date.month,
                year=date.year,
                number=2,
            )

        periods.add(period)

    return sorted(periods)


def get_shift_dates_of_staff(staff_id: int) -> list[datetime.date]:
    return list(
        Shift.objects
        .filter(staff_id=staff_id)
        .values_list("date", flat=True)
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffReportPeriodsReadInteractor:
    staff_id: int

    def execute(self) -> StaffReportPeriods:
        ensure_staff_exists(self.staff_id)
        shift_dates = get_shift_dates_of_staff(self.staff_id)
        report_periods = get_report_periods_of_dates(shift_dates)
        return StaffReportPeriods(
            staff_id=self.staff_id,
            periods=report_periods,
        )


def get_report_period_by_number(
        *,
        year: int,
        month: int,
        report_period_number: int,
) -> ReportPeriod:
    """

    Keyword Args:
        year: year number.
        month: month number, 1-12.
        report_period_number: half of month, 1 or 2.

    Returns:
        Period: Period object.
    """
    is_first_half_of_month = report_period_number == 1
    if is_first_half_of_month:
        from_date = pendulum.date(year, month, 1)
        to_date = pendulum.date(year, month, 15)
    else:
        next_month = pendulum.date(year, month, 1).add(months=1)
        to_date = next_month.start_of("month").subtract(days=1)
        from_date = pendulum.date(year, month, 16)

    return ReportPeriod(
        from_date=from_date,
        to_date=to_date,
        month=month,
        year=year,
        number=report_period_number
    )
