import datetime

import pytest
from django.utils import timezone

from shifts.models import AvailableDate
from shifts.services.shifts import DeadSoulsReadInteractor
from shifts.tests.factories import AvailableDateFactory, ShiftFactory
from staff.tests.factories import StaffFactory


@pytest.fixture
def available_date() -> AvailableDate:
    return AvailableDateFactory(month=1, year=2025)


@pytest.mark.django_db
def test_month_and_year_are_the_same(available_date):
    interactor = DeadSoulsReadInteractor(
        month=available_date.month,
        year=available_date.year,
    )
    staff_without_shifts = interactor.execute()

    assert staff_without_shifts.month == available_date.month
    assert staff_without_shifts.year == available_date.year


@pytest.mark.django_db
def test_staff_without_shifts_for_month(available_date):
    staff = StaffFactory(banned_at=None)
    ShiftFactory(
        staff=staff,
        date=datetime.date(available_date.year, available_date.month, 1),
    )

    interactor = DeadSoulsReadInteractor(
        month=available_date.month,
        year=available_date.year,
    )
    staff_without_shifts = interactor.execute()

    assert not staff_without_shifts.staff_list


@pytest.mark.django_db
def test_staff_without_shifts_for_month_with_staff(available_date):
    staff = StaffFactory(banned_at=None)

    interactor = DeadSoulsReadInteractor(
        month=available_date.month,
        year=available_date.year,
    )
    staff_without_shifts = interactor.execute()

    assert len(staff_without_shifts.staff_list) == 1
    assert staff_without_shifts.staff_list[0].id == staff.id
    assert staff_without_shifts.staff_list[0].full_name == staff.full_name


@pytest.mark.django_db
def test_staff_banned(available_date):
    StaffFactory(banned_at=timezone.now())

    interactor = DeadSoulsReadInteractor(
        month=available_date.month,
        year=available_date.year,
    )
    staff_without_shifts = interactor.execute()

    assert not staff_without_shifts.staff_list
