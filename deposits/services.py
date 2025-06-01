import datetime
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from deposits.models import FineDepositException, RoadAccidentDepositException
from shifts.models import Shift
from shifts.services.report_periods import ReportPeriod


def get_staff_excluded_from_fine_deposit(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
) -> set[int]:
    exceptions = (
        FineDepositException.objects
        .filter(
            from_date__lte=to_date,
            to_date__gte=from_date,
        )
        .values('staff_id')
    )
    return {exception['staff_id'] for exception in exceptions}


def get_staff_excluded_from_road_accident_deposit(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
) -> set[int]:
    exceptions = (
        RoadAccidentDepositException.objects
        .filter(
            from_date__lte=to_date,
            to_date__gte=from_date,
        )
        .values('staff_id')
    )
    return {exception['staff_id'] for exception in exceptions}


def compute_staff_deposit_return_date(
        banned_at: datetime.datetime | None,
) -> datetime.datetime | None:
    if banned_at is None:
        return None
    return banned_at + datetime.timedelta(days=60)


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffReportPeriods:
    staff_id: int
    report_periods_count: int


def get_report_periods_for_staff_ids(
        *,
        staff_ids: Iterable[int],
        until: datetime.date,
) -> list[StaffReportPeriods]:
    shifts = (
        Shift.objects
        .filter(staff_id__in=staff_ids, date__lte=until)
        .values("staff_id", "date")
    )

    staff_id_to_report_periods: dict[int, set[ReportPeriod]] = defaultdict(set)

    for shift in shifts:
        shift_date = shift["date"]
        staff_id = shift["staff_id"]

        half = 1 if shift_date.day <= 15 else 2
        period = ReportPeriod.from_number(
            shift_date.year,
            shift_date.month,
            half,
        )
        staff_id_to_report_periods[staff_id].add(period)

    return [
        StaffReportPeriods(
            staff_id=staff_id,
            report_periods_count=len(report_periods),
        )
        for staff_id, report_periods in staff_id_to_report_periods.items()
    ]
