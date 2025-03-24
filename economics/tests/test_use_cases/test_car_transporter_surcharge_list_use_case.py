import pytest

from economics.tests.factories import CarTransporterSurchargeFactory
from economics.use_cases import CarTransporterSurchargeListUseCase
from economics.use_cases.car_transporter_surcharge_list import (
    SurchargesPage,
    SurchargesPageItem,
)


@pytest.mark.django_db
def test_car_transporter_surcharge_list_empty():
    response = CarTransporterSurchargeListUseCase(
        limit=100,
        offset=0,
    ).execute()

    assert len(response.surcharges) == 0
    assert response.is_end_of_list_reached


@pytest.mark.django_db
def test_car_transporter_surcharge_list_contains_surcharges():
    surcharges = CarTransporterSurchargeFactory.create_batch(5)

    response = CarTransporterSurchargeListUseCase(
        limit=100,
        offset=0,
    ).execute()

    assert len(response.surcharges) == 5
    assert response == SurchargesPage(
        surcharges=sorted(
            [
                SurchargesPageItem(
                    id=surcharge.id,
                    staff_id=surcharge.staff.id,
                    staff_full_name=surcharge.staff.full_name,
                    date=surcharge.date,
                    reason=surcharge.reason,
                    amount=surcharge.amount,
                    created_at=surcharge.created_at,
                )
                for surcharge in surcharges
            ],
            key=lambda surcharge: surcharge.created_at,
            reverse=True,
        ),
        is_end_of_list_reached=True,
    )


@pytest.mark.django_db
def test_has_next_page():
    CarTransporterSurchargeFactory.create_batch(2)

    response = CarTransporterSurchargeListUseCase(
        limit=1,
        offset=0,
    ).execute()

    assert not response.is_end_of_list_reached
