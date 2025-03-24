from dataclasses import dataclass

from economics.exceptions import CarTransporterPenaltyNotFoundError
from economics.models import CarTransporterPenalty


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterPenaltyDeleteUseCase:
    penalty_id: int

    def execute(self) -> None:
        deleted_count, _ = CarTransporterPenalty.objects.filter(
            id=self.penalty_id
        ).delete()
        if deleted_count == 0:
            raise CarTransporterPenaltyNotFoundError
