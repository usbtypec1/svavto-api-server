import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from economics.tests.factories import CarTransporterPenaltyFactory


@pytest.mark.django_db
def test_staff_has_multiple_penalties():
    penalties = CarTransporterPenaltyFactory.create_batch(5)
    client = APIClient()
    url = reverse('economics:car-transporter-penalty-list-create')

    response = client.get(url)

    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data == {
        'penalties':
            [
                {
                    'id': penalty.id,
                    'staff_id': penalty.staff.id,
                    'staff_full_name': penalty.staff.full_name,
                    'date': penalty.date.isoformat(),
                    'consequence': penalty.consequence,
                    'reason': penalty.reason,
                    'amount': penalty.amount,
                    'photo_urls': [],
                    'created_at': timezone.make_aware(
                        timezone.make_naive(penalty.created_at)
                    ).isoformat(),
                }
                for penalty in sorted(
                penalties,
                key=lambda penalty: penalty.created_at,
                reverse=True,
            )
            ],
        'is_end_of_list_reached': True,
    }


@pytest.mark.django_db
def test_staff_has_single_penalty():
    client = APIClient()
    penalty = CarTransporterPenaltyFactory()
    url = reverse('economics:car-transporter-penalty-list-create')

    response = client.get(url)

    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data == {
        'penalties':
            [
                {
                    'id': penalty.id,
                    'staff_id': penalty.staff.id,
                    'staff_full_name': penalty.staff.full_name,
                    'date': penalty.date.isoformat(),
                    'consequence': penalty.consequence,
                    'reason': penalty.reason,
                    'amount': penalty.amount,
                    'photo_urls': [],
                    'created_at': timezone.make_aware(
                        timezone.make_naive(penalty.created_at)
                    ).isoformat(),
                }
            ],
        'is_end_of_list_reached': True,
    }


@pytest.mark.django_db
def test_staff_has_no_penalty():
    client = APIClient()
    url = reverse('economics:car-transporter-penalty-list-create')

    response = client.get(url)

    response_data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert response_data == {
        'penalties': [],
        'is_end_of_list_reached': True,
    }
