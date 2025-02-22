import datetime

import pytest
from django.utils import timezone

from shifts.services.shifts.dead_souls import get_staff_with_one_test_shift
from shifts.tests.factories import ShiftFactory
from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_staff_has_single_regular_shift():
    month: int = 1
    year: int = 2025
    ShiftFactory(date=datetime.date(year, month, 1), is_test=False)

    staff_list = get_staff_with_one_test_shift(year=year, month=month)

    assert not staff_list


@pytest.mark.django_db
def test_staff_has_single_test_shift():
    month: int = 1
    year: int = 2025
    shift = ShiftFactory(date=datetime.date(year, month, 1), is_test=True)

    staff_list = get_staff_with_one_test_shift(year=year, month=month)

    assert len(staff_list) == 1
    assert staff_list[0].id == shift.staff.id
    assert staff_list[0].full_name == shift.staff.full_name


@pytest.mark.django_db
def test_staff_has_multiple_test_shifts():
    month: int = 1
    year: int = 2025
    staff = StaffFactory()
    ShiftFactory(staff=staff, date=datetime.date(year, month, 1), is_test=True)
    ShiftFactory(staff=staff, date=datetime.date(year, month, 2), is_test=True)

    staff_list = get_staff_with_one_test_shift(year=year, month=month)

    assert not staff_list


@pytest.mark.django_db
def test_separate_staff_has_own_single_test_shifts_within_month():
    month: int = 1
    year: int = 2025
    staff_1 = StaffFactory()
    staff_2 = StaffFactory()
    ShiftFactory(
        staff=staff_1,
        date=datetime.date(year, month, 1),
        is_test=True,
    )
    ShiftFactory(
        staff=staff_2,
        date=datetime.date(year, month, 1),
        is_test=True,
    )

    staff_list = get_staff_with_one_test_shift(year=year, month=month)

    assert len(staff_list) == 2
    actual = sorted([(staff.id, staff.full_name) for staff in staff_list])
    expected = sorted(
        [
            (staff_1.id, staff_1.full_name), (staff_2.id, staff_2.full_name)
        ]
    )
    assert actual == expected


@pytest.mark.django_db
def test_staff_has_single_test_shifts_on_separate_months():
    staff = StaffFactory()
    shift = ShiftFactory(
        staff=staff,
        date=datetime.date(2025, 1, 1),
        is_test=True,
    )
    ShiftFactory(
        staff=staff,
        date=datetime.date(2025, 2, 1),
        is_test=True,
    )

    staff_list = get_staff_with_one_test_shift(year=2025, month=1)

    assert len(staff_list) == 1
    assert staff_list[0].id == shift.staff.id
    assert staff_list[0].full_name == shift.staff.full_name


@pytest.mark.django_db
def test_banned_staff_has_shift():
    staff = StaffFactory(banned_at=timezone.now())
    ShiftFactory(staff=staff, date=datetime.date(2025, 1, 1), is_test=True)

    staff_list = get_staff_with_one_test_shift(year=2025, month=1)

    assert not staff_list
