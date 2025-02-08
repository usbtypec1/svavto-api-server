import datetime
from dataclasses import dataclass

from economics.models import Surcharge

__all__ = ('create_surcharge',)


@dataclass(frozen=True, slots=True, kw_only=True)
class SurchargeCreateResult:
    id: int
    staff_id: int
    staff_full_name: str
    shift_id: int
    shift_date: datetime.date
    reason: str
    amount: int
    created_at: datetime.datetime


def create_surcharge(
        *,
        shift_id: int,
        reason: str,
        amount: int,
) -> SurchargeCreateResult:
    """
    Give surcharge to staff member.

    Keyword Args:
        shift_id: shift surcharge is related to.
        reason: reason for surcharge.
        amount: amount of surcharge.

    Returns:
        Surcharge: created surcharge.
    """
    surcharge = Surcharge(
        shift_id=shift_id,
        reason=reason,
        amount=amount,
    )
    surcharge.full_clean()
    surcharge.save()

    return SurchargeCreateResult(
        id=surcharge.id,
        staff_id=surcharge.shift.staff.id,
        staff_full_name=surcharge.shift.staff.full_name,
        shift_id=shift_id,
        shift_date=surcharge.shift.date,
        reason=surcharge.reason,
        amount=surcharge.amount,
        created_at=surcharge.created_at,
    )
