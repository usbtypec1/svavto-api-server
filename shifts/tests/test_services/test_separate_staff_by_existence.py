import pytest

from shifts.services.shifts import separate_staff_by_existence
from staff.tests.factories import StaffFactory


@pytest.fixture
def missing_staff_ids() -> list[int]:
    return [7546245, 234235234, 635623423]


@pytest.mark.django_db
def test_all_passed_staff_exist():
    staff_list = StaffFactory.create_batch(5)
    staff_ids = [staff.id for staff in staff_list]

    separated_staff = separate_staff_by_existence(staff_ids)

    assert sorted(separated_staff.existing_staff_ids) == sorted(staff_ids)
    assert not separated_staff.missing_staff_ids


@pytest.mark.django_db
def test_both_existing_staff_missing_staff(missing_staff_ids):
    staff_list = StaffFactory.create_batch(5)
    existing_staff_ids = [staff.id for staff in staff_list]
    staff_ids = existing_staff_ids + missing_staff_ids

    separated_staff = separate_staff_by_existence(staff_ids)

    assert (
            sorted(separated_staff.existing_staff_ids)
            == sorted(existing_staff_ids)
    )
    assert (
            sorted(separated_staff.missing_staff_ids)
            == sorted(missing_staff_ids)
    )


@pytest.mark.django_db
def test_all_staff_missing(missing_staff_ids):
    separated_staff = separate_staff_by_existence(missing_staff_ids)

    assert not separated_staff.existing_staff_ids
    assert (
            sorted(separated_staff.missing_staff_ids)
            == sorted(missing_staff_ids)
    )
