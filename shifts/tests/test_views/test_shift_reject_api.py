import pytest
from django.urls import reverse
from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.test import APIClient

from shifts.tests.factories import ShiftFactory


@pytest.mark.django_db
def test_shift_successfully_rejected():
    shift = ShiftFactory(rejected_at=None)
    client = APIClient()
    url = reverse('shifts:reject')
    data = {'shift_id': shift.id}
    assert shift.rejected_at is None

    response = client.post(url, data=data, format='json')
    shift.refresh_from_db()

    assert shift.rejected_at is not None
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_shift_not_found():
    client = APIClient()
    url = reverse('shifts:reject')
    data = {'shift_id': 5435}

    response = client.post(url, data=data, format='json')

    expected_data = {
        'errors': [
            {
                'code': 'shift_not_found',
                'detail': _('shift not found'),
            },
        ],
        'type': 'client_error',
    }
    assert response.json() == expected_data
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_shift_successfully_rejected_multiple_times():
    shift = ShiftFactory(rejected_at=None)
    client = APIClient()
    url = reverse('shifts:reject')
    data = {'shift_id': shift.id}
    assert shift.rejected_at is None

    response = client.post(url, data=data, format='json')
    shift.refresh_from_db()

    first_rejected_at = shift.rejected_at
    assert shift.rejected_at is not None
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.post(url, data=data, format='json')
    shift.refresh_from_db()

    assert shift.rejected_at != first_rejected_at
    assert response.status_code == status.HTTP_204_NO_CONTENT
