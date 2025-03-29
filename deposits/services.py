import datetime

from deposits.models import FineDepositException
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


def compute_staff_deposit_return_date(
        banned_at: datetime.datetime | None,
) -> datetime.datetime:
    if banned_at is None:
        return datetime.datetime.now()
    return banned_at + datetime.timedelta(days=60)
