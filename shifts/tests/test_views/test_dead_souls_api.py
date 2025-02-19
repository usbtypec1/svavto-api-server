import datetime

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from shifts.models import AvailableDate
from shifts.tests.factories import AvailableDateFactory, ShiftFactory
from staff.tests.factories import StaffFactory


@pytest.fixture
def available_date() -> AvailableDate:
    return AvailableDateFactory(month=1, year=2025)


@pytest.mark.django_db
def test_no_staff(available_date):
    url = reverse('shifts:dead-souls')
    client = APIClient()

    response = client.get(
        url,
        data={'month': available_date.month, 'year': available_date.year},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'staff_list': [],
        'month': available_date.month,
        'year': available_date.year
    }


@pytest.mark.django_db
def test_all_staff_with_shifts(available_date):
    url = reverse('shifts:dead-souls')
    client = APIClient()

    staff = StaffFactory(banned_at=None)
    ShiftFactory(
        staff=staff,
        date=datetime.date(available_date.year, available_date.month, 1),
    )

    response = client.get(
        url,
        data={'month': available_date.month, 'year': available_date.year},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'staff_list': [],
        'month': available_date.month,
        'year': available_date.year
    }


@pytest.mark.django_db
def test_staff_banned(available_date):
    url = reverse('shifts:dead-souls')
    client = APIClient()

    StaffFactory(banned_at=timezone.now())

    response = client.get(
        url,
        data={'month': available_date.month, 'year': available_date.year},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'staff_list': [],
        'month': available_date.month,
        'year': available_date.year
    }


@pytest.mark.django_db
def test_staff_without_shifts(available_date):
    url = reverse('shifts:dead-souls')
    client = APIClient()

    staff = StaffFactory(banned_at=None)

    response = client.get(
        url,
        data={'month': available_date.month, 'year': available_date.year},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'staff_list': [
            {
                'id': staff.id,
                'full_name': staff.full_name,
            }
        ],
        'month': available_date.month,
        'year': available_date.year
    }


@pytest.mark.django_db
def test_month_not_available():
    url = reverse('shifts:dead-souls')
    client = APIClient()

    response = client.get(
        url,
        data={'month': 1, 'year': 2021},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'errors': [
            {
                'code': 'month_not_available',
                'detail': 'month is not available',
                'extra': {
                    'month': 1,
                    'year': 2021,
                }
            }
        ],
        'type': 'client_error',
    }
