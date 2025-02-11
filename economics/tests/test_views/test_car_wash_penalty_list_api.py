import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from economics.tests.factories import CarWashPenaltyFactory


@pytest.mark.django_db
def test_car_wash_penalty_create_api_without_params():
    penalty = CarWashPenaltyFactory()
    url = reverse('economics:car-wash-penalty-list-create')
    client = APIClient()

    response = client.get(url)

    response_data = response.json()
    penalties = response_data['penalties']

    assert response.status_code == status.HTTP_200_OK
    assert len(penalties) == 1
    penalties[0].pop('created_at')
    assert penalties[0] == {
        'id': penalty.id,
        'car_wash_id': penalty.car_wash_id,
        'reason': penalty.reason,
        'amount': penalty.amount,
    }
