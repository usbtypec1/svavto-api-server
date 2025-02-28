import datetime
from dataclasses import dataclass

from django.core.exceptions import ValidationError

from car_washes.exceptions import CarWashNotFoundError
from economics.models import CarWashSurcharge

__all__ = (
    'CarWashSurchargeCreateInteractor',
    'CarWashSurchargeCreateResult',
    'CarWashSurchargeListInteractor',
    'CarWashSurchargeListItem',
    'CarWashSurchargeDeleteInteractor',
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashSurchargeCreateResult:
    id: int
    car_wash_id: int
    reason: str
    amount: int
    date: datetime.date
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashSurchargeListItem:
    id: int
    car_wash_id: int
    reason: str
    amount: int
    date: datetime.date
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashSurchargeCreateInteractor:
    car_wash_id: int
    reason: str
    amount: int
    date: datetime.date

    def execute(self) -> CarWashSurchargeCreateResult:
        surcharge = CarWashSurcharge(
            car_wash_id=self.car_wash_id,
            reason=self.reason,
            amount=self.amount,
            date=self.date,
        )
        try:
            surcharge.full_clean()
        except ValidationError as error:
            if 'car_wash' in error.message_dict:
                raise CarWashNotFoundError
            raise

        surcharge.save()

        return CarWashSurchargeCreateResult(
            id=surcharge.id,
            car_wash_id=surcharge.car_wash_id,
            reason=surcharge.reason,
            amount=surcharge.amount,
            date=surcharge.date,
            created_at=surcharge.created_at,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashSurchargeListInteractor:
    from_date: datetime.datetime | None
    to_date: datetime.datetime | None
    car_wash_ids: list[int] | None

    def execute(self) -> list[CarWashSurchargeListItem]:
        surcharges = CarWashSurcharge.objects.order_by('-created_at')
        if self.car_wash_ids is not None:
            surcharges = surcharges.filter(car_wash_id__in=self.car_wash_ids)
        if self.from_date is not None:
            surcharges = surcharges.filter(created_at__gte=self.from_date)
        if self.to_date is not None:
            surcharges = surcharges.filter(created_at__lte=self.to_date)

        return [
            CarWashSurchargeListItem(
                id=surcharge.id,
                car_wash_id=surcharge.car_wash_id,
                reason=surcharge.reason,
                amount=surcharge.amount,
                date=surcharge.date,
                created_at=surcharge.created_at,
            )
            for surcharge in surcharges
        ]


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashSurchargeDeleteInteractor:
    surcharge_id: int

    def execute(self) -> None:
        deleted_count, _ = (
            CarWashSurcharge.objects
            .filter(id=self.surcharge_id)
            .delete()
        )
        if deleted_count == 0:
            raise CarWashNotFoundError
