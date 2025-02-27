import datetime

import pytest
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from shifts.tests.factories import ShiftFactory
from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_no_shifts():
    client = APIClient()
    staff = StaffFactory()
    url = reverse('shifts:staff-shifts-month-list', args=[staff.id])

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'staff_id': staff.id,
        'months': []
    }


@pytest.mark.django_db
@freeze_time('2025-01-01')
def test_shifts_in_different_months():
    client = APIClient()
    staff = StaffFactory()
    ShiftFactory(staff=staff, date=datetime.date(2025, 1, 15))
    ShiftFactory(staff=staff, date=datetime.date(2025, 2, 10))
    url = reverse('shifts:staff-shifts-month-list', args=[staff.id])

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'staff_id': staff.id,
        'months': [
            {'month': 1, 'year': 2025},
            {'month': 2, 'year': 2025},
        ]
    }


@pytest.mark.django_db
@freeze_time('2025-01-15')
def test_shifts_in_current_month_before_current_time():
    client = APIClient()
    staff = StaffFactory()
    date = datetime.date(2025, 1, 14)
    ShiftFactory(staff=staff, date=date)
    url = reverse('shifts:staff-shifts-month-list', args=[staff.id])

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'staff_id': staff.id,
        'months': [
            {'month': date.month, 'year': date.year},
        ]
    }


@pytest.mark.django_db
def test_invalid_staff():
    client = APIClient()
    url = reverse('shifts:staff-shifts-month-list', args=[99999])

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['errors'][0]['code'] == 'staff_not_found'
