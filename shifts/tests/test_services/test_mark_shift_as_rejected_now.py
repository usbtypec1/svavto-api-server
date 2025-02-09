import pytest

from shifts.services.shifts import mark_shift_as_rejected_now
from shifts.tests.factories import ShiftFactory


@pytest.mark.django_db
def test_mark_shift_as_rejected_now():
    shift = ShiftFactory(rejected_at=None)
    assert mark_shift_as_rejected_now(shift.id)
    shift.refresh_from_db()
    assert shift.rejected_at is not None
