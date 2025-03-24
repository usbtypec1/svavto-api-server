import pytest

from economics.exceptions import CarTransporterSurchargeNotFoundError
from economics.models import CarTransporterSurcharge
from economics.tests.factories import CarTransporterSurchargeFactory
from economics.use_cases import CarTransporterSurchargeDeleteUseCase


@pytest.mark.django_db
def test_successful_delete():
    surcharge = CarTransporterSurchargeFactory()

    CarTransporterSurchargeDeleteUseCase(surcharge_id=surcharge.id).execute()

    with pytest.raises(CarTransporterSurcharge.DoesNotExist):
        surcharge.refresh_from_db()


@pytest.mark.django_db
def test_delete_non_existent():
    with pytest.raises(CarTransporterSurchargeNotFoundError):
        CarTransporterSurchargeDeleteUseCase(surcharge_id=123423).execute()
