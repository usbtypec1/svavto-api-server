import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from bonuses.tests.factories import BonusSettingsFactory
from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_empty_list():
    url = reverse('bonuses:excluded-staff-list-update')
    client = APIClient()

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'staff_ids': []}


@pytest.mark.django_db
def test_single_staff():
    url = reverse('bonuses:excluded-staff-list-update')
    client = APIClient()
    staff = StaffFactory()
    BonusSettingsFactory().excluded_staff.add(staff)

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'staff_ids': [staff.id]}
