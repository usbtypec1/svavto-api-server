import pytest
import pendulum

from shifts.services.report_periods import (
    get_report_period_by_number,
    ReportPeriod,
)


@pytest.mark.parametrize(
    'year, month, report_period_number, from_date, to_date',
    [
        (
                2025,
                1,
                1,
                pendulum.date(2025, 1, 1),
                pendulum.date(2025, 1, 15),
        ),
        (
                2025,
                1,
                2,
                pendulum.date(2025, 1, 16),
                pendulum.date(2025, 1, 31),
        ),
        (
                2024,
                2,
                2,
                pendulum.date(2024, 2, 16),
                pendulum.date(2024, 2, 29),
        ),
        (
                2025,
                2,
                2,
                pendulum.date(2025, 2, 16),
                pendulum.date(2025, 2, 28),
        ),
        (
                2025,
                4,
                2,
                pendulum.date(2025, 4, 16),
                pendulum.date(2025, 4, 30),
        )
    ]
)
def test_get_report_period_by_number(
        year,
        month,
        report_period_number,
        from_date,
        to_date
):
    assert get_report_period_by_number(
        year=year,
        month=month,
        report_period_number=report_period_number,
    ) == ReportPeriod(
        from_date=from_date,
        to_date=to_date,
        month=month,
        year=year,
        number=report_period_number,
    )
