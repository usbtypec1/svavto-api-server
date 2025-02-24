import pytest

from shifts.exceptions import MonthNotAvailableError
from shifts.services.shifts.dead_souls import ensure_month_is_available
from shifts.tests.factories import AvailableDateFactory


@pytest.mark.django_db
def test_month_is_not_available():
    year = 2021
    month = 1

    with pytest.raises(MonthNotAvailableError) as error:
        ensure_month_is_available(month=month, year=year)

    assert error.value.extra['month'] == month
    assert error.value.extra['year'] == year


@pytest.mark.django_db
def test_month_is_available():
    year = 2021
    month = 1
    AvailableDateFactory(year=year, month=month)

    ensure_month_is_available(month=month, year=year)
