import datetime

import pytest
from django.utils import timezone

from shifts.services.shifts import get_staff_with_no_shifts
from shifts.tests.factories import ShiftFactory
from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_staff_has_no_shifts():
    staff = StaffFactory()

    staff_list = get_staff_with_no_shifts(year=2025, month=1)

    assert len(staff_list) == 1
    assert staff_list[0].id == staff.id
    assert staff_list[0].full_name == staff.full_name


@pytest.mark.django_db
def test_staff_has_shifts_in_selected_month():
    ShiftFactory(date=datetime.date(2025, 1, 1))

    staff_list = get_staff_with_no_shifts(year=2025, month=1)

    assert not staff_list


@pytest.mark.django_db
def test_staff_has_shifts_in_other_month():
    shift = ShiftFactory(date=datetime.date(2025, 2, 1))

    staff_list = get_staff_with_no_shifts(year=2025, month=1)

    assert len(staff_list) == 1
    assert staff_list[0].id == shift.staff.id
    assert staff_list[0].full_name == shift.staff.full_name


@pytest.mark.django_db
def test_banned_staff_has_shift():
    staff = StaffFactory(banned_at=timezone.now())
    ShiftFactory(staff=staff, date=datetime.date(2025, 1, 1))

    staff_list = get_staff_with_no_shifts(year=2025, month=1)

    assert not staff_list
