import pytest

from economics.exceptions import CarTransporterPenaltyNotFoundError
from economics.models import CarTransporterPenalty
from economics.tests.factories import CarTransporterPenaltyFactory
from economics.use_cases import CarTransporterPenaltyDeleteUseCase


@pytest.mark.django_db
def test_successful_delete():
    penalty = CarTransporterPenaltyFactory()

    CarTransporterPenaltyDeleteUseCase(penalty_id=penalty.id).execute()

    with pytest.raises(CarTransporterPenalty.DoesNotExist):
        penalty.refresh_from_db()


@pytest.mark.django_db
def test_delete_non_existent():
    with pytest.raises(CarTransporterPenaltyNotFoundError):
        CarTransporterPenaltyDeleteUseCase(penalty_id=123423).execute()
