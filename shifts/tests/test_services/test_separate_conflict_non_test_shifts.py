import datetime

import pytest

from shifts.services.shifts.create.extra_shift import (
    separate_conflict_non_test_shifts
)
from shifts.tests.factories import ShiftFactory
from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_no_conflict_shifts():
    shift = ShiftFactory(date=datetime.date(2025, 1, 1))

    separated_shifts = separate_conflict_non_test_shifts(
        [
            {
                'staff_id': shift.staff.id,
                'date': datetime.date(2025, 1, 2),
            },
        ]
    )

    assert separated_shifts.non_conflict_shifts == [
        {
            'staff_id': shift.staff.id,
            'date': datetime.date(2025, 1, 2),
        },
    ]
    assert separated_shifts.conflict_shifts == []


@pytest.mark.django_db
def test_all_conflict_shifts():
    shift = ShiftFactory(date=datetime.date(2025, 1, 1))

    separated_shifts = separate_conflict_non_test_shifts(
        [
            {
                'staff_id': shift.staff.id,
                'date': datetime.date(2025, 1, 1),
            },
        ]
    )

    assert separated_shifts.non_conflict_shifts == []
    assert separated_shifts.conflict_shifts == [
        {
            'staff_id': shift.staff.id,
            'date': datetime.date(2025, 1, 1),
        },
    ]


@pytest.mark.django_db
def test_mixed_shifts_of_single_staff():
    shift = ShiftFactory(date=datetime.date(2025, 1, 1))

    separated_shifts = separate_conflict_non_test_shifts(
        [
            {
                'staff_id': shift.staff.id,
                'date': datetime.date(2025, 1, 1),
            },
            {
                'staff_id': shift.staff.id,
                'date': datetime.date(2025, 1, 2),
            },
        ]
    )

    assert separated_shifts.non_conflict_shifts == [
        {
            'staff_id': shift.staff.id,
            'date': datetime.date(2025, 1, 2),
        },
    ]
    assert separated_shifts.conflict_shifts == [
        {
            'staff_id': shift.staff.id,
            'date': datetime.date(2025, 1, 1),
        },
    ]


@pytest.mark.django_db
def test_mixed_shifts_of_multiple_staff():
    staff_1 = StaffFactory()
    staff_2 = StaffFactory()
    ShiftFactory(staff=staff_1, date=datetime.date(2025, 1, 1))
    ShiftFactory(staff=staff_2, date=datetime.date(2025, 1, 1))

    separated_shifts = separate_conflict_non_test_shifts(
        [
            {
                'staff_id': staff_1.id,
                'date': datetime.date(2025, 1, 1),
            },
            {
                'staff_id': staff_2.id,
                'date': datetime.date(2025, 1, 1),
            },
            {
                'staff_id': staff_2.id,
                'date': datetime.date(2025, 1, 2),
            },
        ]
    )

    assert separated_shifts.non_conflict_shifts == [
        {
            'staff_id': staff_2.id,
            'date': datetime.date(2025, 1, 2),
        },
    ]
    assert sorted(
        separated_shifts.conflict_shifts, key=lambda x: x['staff_id']
    ) == sorted(
        [
            {
                'staff_id': staff_1.id,
                'date': datetime.date(2025, 1, 1),
            },
            {
                'staff_id': staff_2.id,
                'date': datetime.date(2025, 1, 1),
            },
        ], key=lambda x: x['staff_id']
    )
