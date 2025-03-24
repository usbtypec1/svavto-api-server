import datetime
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from django.db.models import Sum

from economics.models import (
    CarTransporterPenalty, CarTransporterSurcharge, CarWashPenalty,
    CarWashSurcharge,
)


__all__ = (
    "compute_staff_penalties_count",
    "StaffPenaltiesOrSurchargesForSpecificShift",
    "PenaltyOrSurchargeAmountAndShiftDate",
    "get_car_transporters_penalties_for_period",
    "get_car_transporters_surcharges_for_period",
    "get_car_wash_penalties_and_surcharges_for_period",
    "CarWashPenaltiesAndSurchargesByDate",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class CarWashPenaltiesAndSurchargesByDate:
    date: datetime.date
    penalties_amount: int
    surcharges_amount: int


def get_car_wash_penalties_and_surcharges_for_period(
        *,
        car_wash_ids: Iterable[int],
        from_date: datetime.date,
        to_date: datetime.date,
) -> list[CarWashPenaltiesAndSurchargesByDate]:
    penalties = (
        CarWashPenalty.objects.filter(
            date__range=(from_date, to_date),
            car_wash_id__in=car_wash_ids,
        )
        .values("date")
        .annotate(total_amount=Sum("amount"))
    )
    surcharges = (
        CarWashSurcharge.objects.filter(
            date__range=(from_date, to_date),
            car_wash_id__in=car_wash_ids,
        )
        .values("date")
        .annotate(total_amount=Sum("amount"))
    )

    surcharge_date_to_amount = {
        surcharge["date"]: surcharge["total_amount"] for surcharge in
        surcharges
    }
    penalty_date_to_amount = {
        penalty["date"]: penalty["total_amount"] for penalty in penalties
    }
    dates = set(surcharge_date_to_amount).union(penalty_date_to_amount)

    result: list[CarWashPenaltiesAndSurchargesByDate] = []
    for date in dates:
        penalties_amount = penalty_date_to_amount.get(date, 0)
        surcharges_amount = surcharge_date_to_amount.get(date, 0)

        result.append(
            CarWashPenaltiesAndSurchargesByDate(
                date=date,
                penalties_amount=penalties_amount,
                surcharges_amount=surcharges_amount,
            )
        )

    return result


@dataclass(frozen=True, slots=True)
class PenaltyOrSurchargeAmountAndShiftDate:
    staff_id: int
    shift_date: datetime.date
    total_amount: int


@dataclass(frozen=True, slots=True)
class StaffPenaltiesOrSurchargesForSpecificShift:
    staff_id: int
    items: list[PenaltyOrSurchargeAmountAndShiftDate]


def compute_staff_penalties_count(
        *,
        staff_id: int,
        reason: str,
) -> int:
    """
    Get count of penalties that staff member has with specific reason.

    Args:
        staff_id: staff member's ID.
        reason: reason of penalties.

    Returns:
        Penalties count.
    """
    return (
        CarTransporterPenalty.objects
        .filter(staff_id=staff_id, reason=reason)
        .count()
    )


def group_by_staff_id(
        grouped_by_staff_id_and_shift_date: Iterable[dict],
) -> list[StaffPenaltiesOrSurchargesForSpecificShift]:
    staff_id_to_items = defaultdict(list)
    for staff_id_and_date_and_amount in grouped_by_staff_id_and_shift_date:
        staff_id = staff_id_and_date_and_amount["staff_id"]
        staff_id_to_items[staff_id].append(
            PenaltyOrSurchargeAmountAndShiftDate(
                staff_id=staff_id,
                shift_date=staff_id_and_date_and_amount["date"],
                total_amount=staff_id_and_date_and_amount["total_amount"],
            )
        )
    return [
        StaffPenaltiesOrSurchargesForSpecificShift(
            staff_id=staff_id,
            items=items,
        )
        for staff_id, items in staff_id_to_items.items()
    ]


def get_car_transporters_penalties_for_period(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
        staff_ids: Iterable[int] | None = None,
) -> list[StaffPenaltiesOrSurchargesForSpecificShift]:
    penalties = CarTransporterPenalty.objects.filter(
        date__gte=from_date,
        date__lte=to_date,
    )
    if staff_ids is not None:
        penalties = penalties.filter(staff_id__in=staff_ids)
    penalties_grouped_by_staff_id_and_shift_date = penalties.values(
        "staff_id", "date"
    ).annotate(total_amount=Sum("amount"))
    return group_by_staff_id(penalties_grouped_by_staff_id_and_shift_date)


def get_car_transporters_surcharges_for_period(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
        staff_ids: Iterable[int] | None = None,
) -> list[StaffPenaltiesOrSurchargesForSpecificShift]:
    surcharges = CarTransporterSurcharge.objects.filter(
        date__gte=from_date,
        date__lte=to_date,
    )
    if staff_ids is not None:
        surcharges = surcharges.filter(staff_id__in=staff_ids)
    surcharges_grouped_by_staff_id_and_shift_date = surcharges.values(
        "staff_id", "date"
    ).annotate(total_amount=Sum("amount"))
    return group_by_staff_id(surcharges_grouped_by_staff_id_and_shift_date)
