import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from economics.tests.factories import CarWashSurchargeFactory


@pytest.mark.django_db
def test_car_wash_surcharge_create_api_without_params():
    surcharge = CarWashSurchargeFactory()
    url = reverse('economics:car-wash-surcharge-list-create')
    client = APIClient()

    response = client.get(url)

    response_data = response.json()
    surcharges = response_data['surcharges']

    assert response.status_code == status.HTTP_200_OK
    assert len(surcharges) == 1
    surcharges[0].pop('created_at')
    assert surcharges[0] == {
        'id': surcharge.id,
        'car_wash_id': surcharge.car_wash_id,
        'reason': surcharge.reason,
        'amount': surcharge.amount,
        'date': str(surcharge.date),
    }
