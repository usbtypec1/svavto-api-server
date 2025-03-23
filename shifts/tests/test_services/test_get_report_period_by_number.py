import pytest
import pendulum

from shifts.services.report_periods import get_report_period_by_number, Period


@pytest.mark.parametrize(
    'year, month, report_period_number, period',
    [
        (2025, 1, 1, Period(
            from_date=pendulum.date(2025, 1, 1),
            to_date=pendulum.date(2025, 1, 15),
        )),
        (2025, 1, 2, Period(
            from_date=pendulum.date(2025, 1, 16),
            to_date=pendulum.date(2025, 1, 31),
        )),
        (2024, 2, 2, Period(
            from_date=pendulum.date(2024, 2, 16),
            to_date=pendulum.date(2024, 2, 29),
        )),
        (2025, 2, 2, Period(
            from_date=pendulum.date(2025, 2, 16),
            to_date=pendulum.date(2025, 2, 28),
        )),
        (2025, 4, 2, Period(
            from_date=pendulum.date(2025, 4, 16),
            to_date=pendulum.date(2025, 4, 30),
        ))
    ]
)
def test_get_report_period_by_number(
        year,
        month,
        report_period_number,
        period,
):
    assert get_report_period_by_number(
        year=year,
        month=month,
        report_period_number=report_period_number,
    ) == period
