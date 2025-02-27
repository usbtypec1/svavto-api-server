import datetime

import pytest
from freezegun import freeze_time

from shifts.services import StaffShiftsMonthListInteractor
from shifts.tests.factories import ShiftFactory
from staff.exceptions import StaffNotFoundError
from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_staff_not_found():
    with pytest.raises(StaffNotFoundError):
        StaffShiftsMonthListInteractor(staff_id=1).execute()


@pytest.mark.django_db
def test_response_staff_id_is_the_same():
    staff = StaffFactory()

    staff_shifts_months = StaffShiftsMonthListInteractor(
        staff_id=staff.id,
    ).execute()

    assert staff_shifts_months.staff_id == staff.id


@pytest.mark.django_db
@freeze_time('2025-01-01')
def test_staff_has_single_shift_month():
    date = datetime.date(2025, 2, 1)
    shift = ShiftFactory(date=date)

    staff_shifts_months = StaffShiftsMonthListInteractor(
        staff_id=shift.staff.id,
    ).execute()

    assert len(staff_shifts_months.months) == 1
    assert staff_shifts_months.months[0].year == date.year
    assert staff_shifts_months.months[0].month == date.month


@pytest.mark.django_db
@freeze_time('2025-01-01')
def test_staff_has_no_shift_month():
    staff = StaffFactory()
    staff_shifts_months = StaffShiftsMonthListInteractor(
        staff_id=staff.id,
    ).execute()

    assert len(staff_shifts_months.months) == 0


@pytest.mark.django_db
@freeze_time('2025-01-01')
def test_staff_has_multiple_shift_months():
    staff = StaffFactory()
    ShiftFactory(staff=staff, date=datetime.date(2025, 2, 1))
    ShiftFactory(staff=staff, date=datetime.date(2025, 3, 1))

    staff_shifts_months = StaffShiftsMonthListInteractor(
        staff_id=staff.id,
    ).execute()

    assert len(staff_shifts_months.months) == 2
    assert staff_shifts_months.months[0].year == 2025
    assert staff_shifts_months.months[0].month == 2
    assert staff_shifts_months.months[1].year == 2025
    assert staff_shifts_months.months[1].month == 3


@pytest.mark.django_db
@freeze_time('2025-01-01')
def test_staff_has_multiple_shifts_within_same_month():
    staff = StaffFactory()
    ShiftFactory(staff=staff, date=datetime.date(2025, 2, 1))
    ShiftFactory(staff=staff, date=datetime.date(2025, 2, 2))

    staff_shifts_months = StaffShiftsMonthListInteractor(
        staff_id=staff.id,
    ).execute()

    assert len(staff_shifts_months.months) == 1
    assert staff_shifts_months.months[0].year == 2025
    assert staff_shifts_months.months[0].month == 2


@pytest.mark.django_db
@freeze_time('2025-02-01')
def test_staff_had_shifts_before_but_has_no_shift_now():
    staff = StaffFactory()
    date = datetime.date(2025, 1, 1)
    ShiftFactory(staff=staff, date=date)

    staff_shifts_months = StaffShiftsMonthListInteractor(
        staff_id=staff.id,
    ).execute()

    assert len(staff_shifts_months.months) == 0


@pytest.mark.django_db
@freeze_time('2025-02-01')
def test_staff_had_shifts_before_and_has_shift_now():
    staff = StaffFactory()
    ShiftFactory(staff=staff, date=datetime.date(2025, 1, 31))
    ShiftFactory(staff=staff, date=datetime.date(2025, 2, 1))
    ShiftFactory(staff=staff, date=datetime.date(2025, 3, 15))

    staff_shifts_months = StaffShiftsMonthListInteractor(
        staff_id=staff.id,
    ).execute()

    assert len(staff_shifts_months.months) == 2
    assert staff_shifts_months.months[0].year == 2025
    assert staff_shifts_months.months[0].month == 2
    assert staff_shifts_months.months[1].year == 2025
    assert staff_shifts_months.months[1].month == 3


@pytest.mark.django_db
@freeze_time('2025-02-15')
def test_shifts_in_current_month_before_current_time():
    staff = StaffFactory()
    ShiftFactory(staff=staff, date=datetime.date(2025, 2, 1))

    staff_shifts_months = StaffShiftsMonthListInteractor(
        staff_id=staff.id,
    ).execute()

    assert len(staff_shifts_months.months) == 1
    assert staff_shifts_months.months[0].year == 2025
    assert staff_shifts_months.months[0].month == 2