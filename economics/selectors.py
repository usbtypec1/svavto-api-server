import datetime
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from django.db.models import Sum

from economics.models import Penalty, StaffServicePrice, Surcharge
from shifts.exceptions import StaffServicePriceNotFoundError
from shifts.models import CarToWash

__all__ = (
    'compute_car_transfer_price',
    'compute_staff_penalties_count',
    'StaffPenaltiesOrSurchargesForSpecificShift',
    'PenaltyOrSurchargeAmountAndShiftDate',
    'get_penalties_for_period',
    'get_surcharges_for_period',
)


@dataclass(frozen=True, slots=True)
class PenaltyOrSurchargeAmountAndShiftDate:
    staff_id: int
    shift_date: datetime.date
    total_amount: int


@dataclass(frozen=True, slots=True)
class StaffPenaltiesOrSurchargesForSpecificShift:
    staff_id: int
    items: list[PenaltyOrSurchargeAmountAndShiftDate]


def compute_car_transfer_price(
        *,
        class_type: str,
        wash_type: str,
        is_extra_shift: bool,
) -> int:
    if wash_type == CarToWash.WashType.URGENT:
        service_name = StaffServicePrice.ServiceType.URGENT_CAR_WASH
    else:
        if is_extra_shift:
            service_name = (
                StaffServicePrice.ServiceType.CAR_TRANSPORTER_EXTRA_SHIFT
            )
        else:
            car_class_type_to_service_name: dict[str, str] = {
                CarToWash.CarType.COMFORT:
                    StaffServicePrice.ServiceType.COMFORT_CLASS_CAR_TRANSFER,
                CarToWash.CarType.BUSINESS:
                    StaffServicePrice.ServiceType.BUSINESS_CLASS_CAR_TRANSFER,
                CarToWash.CarType.VAN:
                    StaffServicePrice.ServiceType.VAN_TRANSFER,
            }
            service_name = car_class_type_to_service_name[class_type]

    try:
        staff_service_price = StaffServicePrice.objects.get(
            service=service_name
        )
    except StaffServicePrice.DoesNotExist:
        raise StaffServicePriceNotFoundError
    return staff_service_price.price


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
    return Penalty.objects.filter(staff_id=staff_id, reason=reason).count()


def group_by_staff_id(
        grouped_by_staff_id_and_shift_date: Iterable[dict],
) -> list[StaffPenaltiesOrSurchargesForSpecificShift]:
    staff_id_to_items = defaultdict(list)
    for staff_id_and_date_and_amount in grouped_by_staff_id_and_shift_date:
        staff_id = staff_id_and_date_and_amount['staff_id']
        staff_id_to_items[staff_id].append(
            PenaltyOrSurchargeAmountAndShiftDate(
                staff_id=staff_id,
                shift_date=staff_id_and_date_and_amount['shift__date'],
                total_amount=staff_id_and_date_and_amount['total_amount'],
            )
        )
    return [
        StaffPenaltiesOrSurchargesForSpecificShift(
            staff_id=staff_id,
            items=items,
        )
        for staff_id, items in staff_id_to_items.items()
    ]


def get_penalties_for_period(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
        staff_ids: Iterable[int] | None = None,
) -> list[StaffPenaltiesOrSurchargesForSpecificShift]:
    penalties = Penalty.objects.filter(
        shift__date__gte=from_date,
        shift__date__lte=to_date,
    )
    if staff_ids is not None:
        penalties = penalties.filter(staff_id__in=staff_ids)
    penalties_grouped_by_staff_id_and_shift_date = (
        penalties
        .values('staff_id', 'shift__date')
        .annotate(total_amount=Sum('amount'))
    )
    return group_by_staff_id(penalties_grouped_by_staff_id_and_shift_date)


def get_surcharges_for_period(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
        staff_ids: Iterable[int] | None = None,
) -> list[StaffPenaltiesOrSurchargesForSpecificShift]:
    surcharges = Surcharge.objects.filter(
        shift__date__gte=from_date,
        shift__date__lte=to_date,
    )
    if staff_ids is not None:
        surcharges = surcharges.filter(staff_id__in=staff_ids)
    surcharges_grouped_by_staff_id_and_shift_date = (
        surcharges
        .values('staff_id', 'shift__date')
        .annotate(total_amount=Sum('amount'))
    )
    return group_by_staff_id(surcharges_grouped_by_staff_id_and_shift_date)
