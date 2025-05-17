import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.translation import gettext as _

from car_washes.tests.factories import CarWashFactory


@pytest.mark.django_db
def test_car_wash_successfully_deleted():
    client = APIClient()
    car_wash = CarWashFactory()
    url = reverse('car-washes:detail-update-delete', args=(car_wash.id,))

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_car_wash_not_found():
    client = APIClient()
    url = reverse('car-washes:detail-update-delete', args=(999,))

    response = client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data == {
        "type": "client_error",
        "errors": [
            {
                "code": "car_wash_not_found",
                "detail": _("car wash was not found"),
            }
        ]
    }