import datetime

from deposits.models import FineDepositException, RoadAccidentDepositException
from staff.models import Staff


def get_fine_deposit_exceptions_for_report_period(
        *,
        year: int,
        month: int,
        report_period_number: int,
) -> list[Staff]:
    exceptions = (
        FineDepositException.objects
        .filter(
            year=year,
            month=month,
            report_period_number=report_period_number,
        )
        .only('staff')
        .all()
    )
    return [
        exception.staff
        for exception in exceptions
    ]


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
