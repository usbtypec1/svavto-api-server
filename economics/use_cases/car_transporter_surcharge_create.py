import datetime
from dataclasses import dataclass

from economics.models import CarTransporterSurcharge
from staff.selectors import get_staff_by_id


@dataclass(frozen=True, slots=True, kw_only=True)
class SurchargeCreateResult:
    id: int
    staff_id: int
    staff_full_name: str
    date: datetime.date
    reason: str
    amount: int
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterSurchargeCreateUseCase:
    """
    Give surcharge to staff member.

    Args:
        staff_id: staff member id.
        date: date surcharge create for.
        reason: reason for surcharge.
        amount: amount of surcharge.

    Returns:
        CarTransporterSurcharge: created surcharge.
    """
    staff_id: int
    date: datetime.date
    reason: str
    amount: int

    def execute(self) -> SurchargeCreateResult:
        staff = get_staff_by_id(self.staff_id)
        surcharge = CarTransporterSurcharge(
            staff_id=staff.id,
            date=self.date,
            reason=self.reason,
            amount=self.amount,
        )
        surcharge.full_clean()
        surcharge.save()

        return SurchargeCreateResult(
            id=surcharge.id,
            staff_id=staff.id,
            staff_full_name=staff.full_name,
            date=surcharge.date,
            reason=surcharge.reason,
            amount=surcharge.amount,
            created_at=surcharge.created_at,
        )
