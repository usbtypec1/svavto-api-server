import datetime

import pytest
from freezegun import freeze_time

from shifts.exceptions import InvalidTimeToStartShiftError
from shifts.services.shifts.validators import ensure_time_to_start_shift


@pytest.mark.parametrize(
    'freeze_at',
    [
        datetime.datetime(2021, 1, 1, 18, 30),
        datetime.datetime(2021, 1, 1, 23, 59),
        datetime.datetime(2021, 1, 2, 5),
        datetime.datetime(2021, 1, 2, 9),
        datetime.datetime(2021, 1, 25, 18, 30),
        datetime.datetime(2021, 1, 25, 23, 59),
        datetime.datetime(2021, 1, 25, 5),
        datetime.datetime(2021, 1, 25, 9),
    ]
)
def test_ensure_time_to_start_shift(freeze_at):
    with freeze_time(freeze_at):
        ensure_time_to_start_shift()


@pytest.mark.parametrize(
    'freeze_at',
    [
        datetime.datetime(2021, 1, 1, 18, 29),
        datetime.datetime(2021, 1, 2, 9, 1),
        datetime.datetime(2021, 1, 2, 10, 15),
        datetime.datetime(2021, 1, 2, 15, 25),
    ]
)
def test_invalid_time_to_start_shift(freeze_at):
    with freeze_time(freeze_at):
        with pytest.raises(InvalidTimeToStartShiftError):
            ensure_time_to_start_shift()
