import pytest

from economics.tests.factories import CarTransporterPenaltyFactory
from economics.use_cases import CarTransporterPenaltyListUseCase
from economics.use_cases.car_transporter_penalty_list import (
    PenaltiesPage,
    PenaltiesPageItem,
)


@pytest.mark.django_db
def test_car_transporter_penalty_list_empty():
    response = CarTransporterPenaltyListUseCase(
        limit=100,
        offset=0,
    ).execute()

    assert len(response.penalties) == 0
    assert response.is_end_of_list_reached


@pytest.mark.django_db
def test_car_transporter_penalty_list_contains_penalties():
    penalties = CarTransporterPenaltyFactory.create_batch(5)

    response = CarTransporterPenaltyListUseCase(
        limit=100,
        offset=0,
    ).execute()

    assert len(response.penalties) == 5
    assert response == PenaltiesPage(
        penalties=sorted(
            [
                PenaltiesPageItem(
                    id=penalty.id,
                    staff_id=penalty.staff.id,
                    staff_full_name=penalty.staff.full_name,
                    date=penalty.date,
                    reason=penalty.reason,
                    amount=penalty.amount,
                    consequence=None,
                    photo_urls=[],
                    created_at=penalty.created_at,
                )
                for penalty in penalties
            ],
            key=lambda penalty: penalty.created_at,
            reverse=True,
        ),
        is_end_of_list_reached=True,
    )


@pytest.mark.django_db
def test_has_next_page():
    CarTransporterPenaltyFactory.create_batch(2)

    response = CarTransporterPenaltyListUseCase(
        limit=1,
        offset=0,
    ).execute()

    assert not response.is_end_of_list_reached
