import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from bonuses.models import BonusSettings
from bonuses.tests.factories import BonusSettingsFactory
from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_erase_excluded_staff_list():
    url = reverse('bonuses:excluded-staff-list-update')
    client = APIClient()
    staff = StaffFactory()
    settings = BonusSettingsFactory()
    settings.excluded_staff.add(staff)

    response = client.put(url, data={'staff_ids': []}, format='json')
    settings.refresh_from_db()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not settings.excluded_staff.exists()


@pytest.mark.django_db
def test_single_staff():
    url = reverse('bonuses:excluded-staff-list-update')
    client = APIClient()
    staff = StaffFactory()
    settings = BonusSettingsFactory()

    response = client.put(url, data={'staff_ids': [staff.id]}, format='json')
    settings.refresh_from_db()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert settings.excluded_staff.count() == 1
    assert settings.excluded_staff.first().id == staff.id
