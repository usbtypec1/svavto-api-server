import datetime
from dataclasses import dataclass

from django.core.exceptions import ValidationError

from car_washes.exceptions import CarWashNotFoundError
from economics.models import CarWashPenalty

__all__ = (
    'CarWashPenaltyCreateInteractor',
    'CarWashPenaltyCreateResult',
    'CarWashPenaltyListInteractor',
    'CarWashPenaltyListItem',
    'CarWashPenaltyDeleteInteractor',
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashPenaltyCreateResult:
    id: int
    car_wash_id: int
    reason: str
    amount: int
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashPenaltyListItem:
    id: int
    car_wash_id: int
    reason: str
    amount: int
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashPenaltyCreateInteractor:
    car_wash_id: int
    reason: str
    amount: int

    def execute(self) -> CarWashPenaltyCreateResult:
        penalty = CarWashPenalty(
            car_wash_id=self.car_wash_id,
            reason=self.reason,
            amount=self.amount,
        )
        try:
            penalty.full_clean()
        except ValidationError as error:
            if 'car_wash' in error.message_dict:
                raise CarWashNotFoundError
            raise

        penalty.save()

        return CarWashPenaltyCreateResult(
            id=penalty.id,
            car_wash_id=penalty.car_wash_id,
            reason=penalty.reason,
            amount=penalty.amount,
            created_at=penalty.created_at,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashPenaltyListInteractor:
    from_date: datetime.datetime | None
    to_date: datetime.datetime | None
    car_wash_ids: list[int] | None

    def execute(self) -> list[CarWashPenaltyListItem]:
        penalties = CarWashPenalty.objects.order_by('-created_at')
        if self.car_wash_ids is not None:
            penalties = penalties.filter(car_wash_id__in=self.car_wash_ids)
        if self.from_date is not None:
            penalties = penalties.filter(created_at__gte=self.from_date)
        if self.to_date is not None:
            penalties = penalties.filter(created_at__lte=self.to_date)

        return [
            CarWashPenaltyListItem(
                id=penalty.id,
                car_wash_id=penalty.car_wash_id,
                reason=penalty.reason,
                amount=penalty.amount,
                created_at=penalty.created_at,
            )
            for penalty in penalties
        ]


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashPenaltyDeleteInteractor:
    penalty_id: int

    def execute(self) -> None:
        deleted_count, _ = (
            CarWashPenalty.objects
            .filter(id=self.penalty_id)
            .delete()
        )
        if deleted_count == 0:
            raise CarWashNotFoundError
