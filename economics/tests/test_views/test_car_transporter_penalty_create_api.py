import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_successfully_created():
    client = APIClient()
    url = reverse('economics:car-transporter-penalty-list-create')
    staff = StaffFactory()

    response = client.post(
        url,
        data={
            'staff_id': staff.id,
            'date': '2025-01-01',
            'reason': 'test',
            'amount': 100,
        },
        format='json'
    )

    response_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert response_data == {
        'id': response_data['id'],
        'staff_id': staff.id,
        'staff_full_name': staff.full_name,
        'date': '2025-01-01',
        'reason': 'test',
        'amount': 100,
        'consequence': None,
        'created_at': response_data['created_at'],
    }


@pytest.mark.django_db
def test_staff_not_found():
    client = APIClient()
    url = reverse('economics:car-transporter-penalty-list-create')

    response = client.post(
        url,
        data={
            'staff_id': 1,
            'date': '2025-01-01',
            'reason': 'test',
            'amount': 100,
        },
        format='json'
    )

    response_data = response.json()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data == {
        'errors': [
            {
                'code': 'staff_not_found',
                'detail': 'Сотрудник не найден',
            },
        ],
        'type': 'client_error',
    }
