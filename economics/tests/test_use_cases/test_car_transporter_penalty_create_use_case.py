import datetime

import pytest

from economics.use_cases import CarTransporterPenaltyCreateUseCase
from economics.use_cases.car_transporter_penalty_create import (
    PenaltyCreateResult
)
from staff.exceptions import StaffNotFoundError
from staff.tests.factories import StaffFactory


@pytest.mark.django_db
def test_successfully_created():
    staff = StaffFactory()
    date = datetime.date(2025, 1, 1)

    penalty = CarTransporterPenaltyCreateUseCase(
        staff_id=staff.id,
        date=date,
        reason='test',
        amount=100,
        photo_urls=[],
    ).execute()

    assert penalty == PenaltyCreateResult(
        id=penalty.id,
        staff_id=staff.id,
        staff_full_name=staff.full_name,
        date=date,
        reason='test',
        amount=100,
        consequence=penalty.consequence,
        photo_urls=[],
        created_at=penalty.created_at,
    )


@pytest.mark.django_db
def test_staff_not_found():
    with pytest.raises(StaffNotFoundError):
        CarTransporterPenaltyCreateUseCase(
            staff_id=5345234234,
            date=datetime.date(2025, 1, 1),
            reason='test',
            amount=100,
            photo_urls=[],
        ).execute()
