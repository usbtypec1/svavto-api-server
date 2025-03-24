from dataclasses import dataclass

from economics.exceptions import CarTransporterSurchargeNotFoundError
from economics.models import CarTransporterSurcharge


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterSurchargeDeleteUseCase:
    surcharge_id: int

    def execute(self) -> None:
        deleted_count, _ = CarTransporterSurcharge.objects.filter(
            id=self.surcharge_id
        ).delete()
        if deleted_count == 0:
            raise CarTransporterSurchargeNotFoundError
