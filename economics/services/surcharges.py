from dataclasses import dataclass
from datetime import datetime

from economics.models import Surcharge

__all__ = ('create_surcharge',)


@dataclass(frozen=True, slots=True)
class SurchargeCreateResult:
    id: int
    staff_id: int
    reason: str
    amount: int
    created_at: datetime


def create_surcharge(
        *,
        staff_id: int,
        reason: str,
        amount: int,
) -> SurchargeCreateResult:
    surcharge = Surcharge.objects.create(
        staff_id=staff_id,
        reason=reason,
        amount=amount,
    )
    return SurchargeCreateResult(
        id=surcharge.id,
        staff_id=surcharge.staff_id,
        reason=surcharge.reason,
        amount=surcharge.amount,
        created_at=surcharge.created_at,
    )
