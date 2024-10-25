from datetime import datetime, UTC, timedelta

import pytest
from django.utils import timezone

from staff.tests.factories import StaffFactory


@pytest.mark.django_db
class TestStaffModel:
    def test_staff_factory_default(self):
        staff = StaffFactory()
        assert staff.id >= 1000
        assert len(staff.full_name) > 0
        assert len(staff.car_sharing_phone_number) > 0
        assert len(staff.console_phone_number) > 0
        assert staff.banned_at is None
        assert staff.created_at is not None
        assert staff.last_activity_at is not None
        assert not staff.is_banned

    def test_staff_factory_banned(self):
        staff = StaffFactory(banned=True)
        assert staff.banned_at is not None
        assert staff.is_banned

    def test_staff_factory_custom_values(self):
        custom_date = datetime.now(UTC) - timedelta(days=10)
        staff = StaffFactory(
            full_name="John Doe",
            car_sharing_phone_number="+1234567890",
            console_phone_number="+0987654321",
            created_at=custom_date
        )
        assert staff.full_name == "John Doe"
        assert staff.car_sharing_phone_number == "+1234567890"
        assert staff.console_phone_number == "+0987654321"
        assert staff.created_at.date() == custom_date.date()

    def test_staff_phone_numbers_max_length(self):
        staff = StaffFactory()
        assert len(staff.car_sharing_phone_number) <= 16
        assert len(staff.console_phone_number) <= 16

    def test_staff_full_name_max_length(self):
        staff = StaffFactory()
        assert len(staff.full_name) <= 100

    @pytest.mark.parametrize('banned_status,expected_banned', [
        (None, False),
        (timezone.now(), True),
        (timezone.now() - timedelta(days=30), True),
    ])
    def test_staff_is_banned_property(self, banned_status, expected_banned):
        staff = StaffFactory(banned_at=banned_status)
        assert staff.is_banned == expected_banned
