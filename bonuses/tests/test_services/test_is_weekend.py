import datetime

import pytest

from bonuses.services import is_weekend


@pytest.mark.parametrize(
    "date,result",
    [
        (datetime.date(2025, 4, 4), False),
        (datetime.date(2025, 4, 5), True),
        (datetime.date(2025, 4, 6), True),
        (datetime.date(2025, 4, 7), False),
        (datetime.date(2025, 4, 8), False),
        (datetime.date(2025, 4, 9), False),
        (datetime.date(2025, 4, 10), False),
        (datetime.date(2025, 4, 11), False),
        (datetime.date(2025, 4, 12), True),
        (datetime.date(2025, 4, 13), True),
        (datetime.date(2025, 4, 14), False),
        (datetime.date(2025, 4, 15), False),
        (datetime.date(2025, 4, 16), False),
        (datetime.date(2025, 4, 17), False),
        (datetime.date(2025, 4, 18), False),
        (datetime.date(2025, 4, 19), True),
        (datetime.date(2025, 4, 20), True),
        (datetime.date(2025, 4, 21), False),
    ]
)
def test_is_weekend(date, result):
    assert is_weekend(date) == result
