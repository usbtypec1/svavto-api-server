import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.translation import gettext as _


@pytest.mark.django_db
def test_car_wash_not_found():
    client = APIClient()
    url = reverse('car-washes:detail-update-delete', args=(53443,))

    response = client.put(url)

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
