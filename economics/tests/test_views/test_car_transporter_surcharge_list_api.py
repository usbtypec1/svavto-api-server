import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from economics.tests.factories import CarTransporterSurchargeFactory


@pytest.mark.django_db
def test_staff_has_multiple_surcharges():
    surcharges = CarTransporterSurchargeFactory.create_batch(5)
    client = APIClient()
    url = reverse('economics:car-transporter-surcharge-list-create')

    response = client.get(url)

    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data == {
        'surcharges':
            [
                {
                    'id': surcharge.id,
                    'staff_id': surcharge.staff.id,
                    'staff_full_name': surcharge.staff.full_name,
                    'date': surcharge.date.isoformat(),
                    'reason': surcharge.reason,
                    'amount': surcharge.amount,
                    'created_at': timezone.make_aware(
                        timezone.make_naive(surcharge.created_at)
                    ).isoformat(),
                }
                for surcharge in sorted(
                surcharges,
                key=lambda surcharge: surcharge.created_at,
                reverse=True,
            )
            ],
        'is_end_of_list_reached': True,
    }


@pytest.mark.django_db
def test_staff_has_single_surcharge():
    client = APIClient()
    surcharge = CarTransporterSurchargeFactory()
    url = reverse('economics:car-transporter-surcharge-list-create')

    response = client.get(url)

    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data == {
        'surcharges':
            [
                {
                    'id': surcharge.id,
                    'staff_id': surcharge.staff.id,
                    'staff_full_name': surcharge.staff.full_name,
                    'date': surcharge.date.isoformat(),
                    'reason': surcharge.reason,
                    'amount': surcharge.amount,
                    'created_at': timezone.make_aware(
                        timezone.make_naive(surcharge.created_at)
                    ).isoformat(),
                }
            ],
        'is_end_of_list_reached': True,
    }


@pytest.mark.django_db
def test_staff_has_no_surcharge():
    client = APIClient()
    url = reverse('economics:car-transporter-surcharge-list-create')

    response = client.get(url)

    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data == {
        'surcharges': [],
        'is_end_of_list_reached': True,
    }
