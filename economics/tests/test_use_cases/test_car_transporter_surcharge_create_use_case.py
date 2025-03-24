import datetime

import pytest

from economics.use_cases import CarTransporterSurchargeCreateUseCase
from economics.use_cases.car_transporter_surcharge_create import (
    SurchargeCreateResult
)
from staff.exceptions import StaffNotFoundError
from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_successfully_created():
    staff = StaffFactory()
    date = datetime.date(2025, 1, 1)

    surcharge = CarTransporterSurchargeCreateUseCase(
        staff_id=staff.id,
        date=date,
        reason='test',
        amount=100,
    ).execute()

    assert surcharge == SurchargeCreateResult(
        id=surcharge.id,
        staff_id=staff.id,
        staff_full_name=staff.full_name,
        date=date,
        reason='test',
        amount=100,
        created_at=surcharge.created_at,
    )


@pytest.mark.django_db
def test_staff_not_found():
    with pytest.raises(StaffNotFoundError):
        CarTransporterSurchargeCreateUseCase(
            staff_id=1432563452,
            date=datetime.date(2025, 1, 1),
            reason='test',
            amount=100,
        ).execute()
