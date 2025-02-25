import datetime
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from django.db.models import Sum
from django.db.models.functions import TruncDate

from economics.models import (
    CarWashPenalty, CarWashSurcharge, Penalty, PenaltyPhoto, StaffServicePrice,
    Surcharge,
)
from shifts.exceptions import StaffServicePriceNotFoundError
from shifts.models import CarToWash


__all__ = (
    'compute_car_transfer_price',
    'compute_staff_penalties_count',
    'StaffPenaltiesOrSurchargesForSpecificShift',
    'PenaltyOrSurchargeAmountAndShiftDate',
    'get_penalties_for_period',
    'get_surcharges_for_period',
    'get_surcharges_page',
    'SurchargesPage',
    'SurchargesPageItem',
    'map_surcharges_to_page_items',
    'get_penalties_page',
    'map_penalties_to_page_items',
    'PenaltiesPage',
    'PenaltiesPageItem',
    'get_car_wash_penalties_and_surcharges_for_period',
    'CarWashPenaltiesAndSurchargesByDate',
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
        CarWashPenalty.objects
        .filter(
            created_at__range=(from_date, to_date),
            car_wash_id__in=car_wash_ids,
        )
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(total_amount=Sum('amount'))
    )
    surcharges = (
        CarWashSurcharge.objects
        .filter(
            created_at__range=(from_date, to_date),
            car_wash_id__in=car_wash_ids,
        )
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(total_amount=Sum('amount'))
    )

    surcharge_date_to_amount = {
        surcharge['date']: surcharge['total_amount']
        for surcharge in surcharges
    }
    penalty_date_to_amount = {
        penalty['date']: penalty['total_amount']
        for penalty in penalties
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
    return (
        Penalty.objects
        .filter(shift__staff_id=staff_id, reason=reason)
        .count()
    )


def group_by_staff_id(
        grouped_by_staff_id_and_shift_date: Iterable[dict],
) -> list[StaffPenaltiesOrSurchargesForSpecificShift]:
    staff_id_to_items = defaultdict(list)
    for staff_id_and_date_and_amount in grouped_by_staff_id_and_shift_date:
        staff_id = staff_id_and_date_and_amount['shift__staff_id']
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
        penalties = penalties.filter(shift__staff_id__in=staff_ids)
    penalties_grouped_by_staff_id_and_shift_date = (
        penalties
        .values('shift__staff_id', 'shift__date')
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
        surcharges = surcharges.filter(shift__staff_id__in=staff_ids)
    surcharges_grouped_by_staff_id_and_shift_date = (
        surcharges
        .values('shift__staff_id', 'shift__date')
        .annotate(total_amount=Sum('amount'))
    )
    return group_by_staff_id(surcharges_grouped_by_staff_id_and_shift_date)


@dataclass(frozen=True, slots=True, kw_only=True)
class SurchargesPageItem:
    id: int
    staff_id: int
    staff_full_name: str
    shift_id: int
    shift_date: datetime.date
    reason: str
    amount: int
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SurchargesPage:
    surcharges: list[SurchargesPageItem]
    is_end_of_list_reached: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class PenaltiesPageItem:
    id: int
    staff_id: int
    staff_full_name: str
    shift_id: int
    shift_date: datetime.date
    consequence: str | None
    reason: str
    amount: int
    photo_urls: list[str]
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class PenaltiesPage:
    penalties: list[PenaltiesPageItem]
    is_end_of_list_reached: bool


def map_surcharges_to_page_items(
        surcharges: Iterable[Surcharge],
) -> list[SurchargesPageItem]:
    return [
        SurchargesPageItem(
            id=surcharge.id,
            staff_id=surcharge.shift.staff.id,
            staff_full_name=surcharge.shift.staff.full_name,
            shift_id=surcharge.shift_id,
            shift_date=surcharge.shift.date,
            reason=surcharge.reason,
            amount=surcharge.amount,
            created_at=surcharge.created_at,
        )
        for surcharge in surcharges
    ]


def get_surcharges_page(
        *,
        staff_ids: Iterable[int] | None = None,
        limit: int,
        offset: int,
) -> SurchargesPage:
    surcharges = (
        Surcharge.objects
        .select_related('shift', 'shift__staff')
        .order_by('-created_at')
        .only(
            'id',
            'shift__staff__id',
            'shift__staff__full_name',
            'shift_id',
            'shift__date',
            'reason',
            'amount',
            'created_at',
        )
    )
    if staff_ids is not None:
        surcharges = surcharges.filter(shift__staff_id__in=staff_ids)
    surcharges = surcharges[offset: offset + limit + 1]

    is_end_of_list_reached = len(surcharges) <= limit
    surcharges = surcharges[:limit]

    return SurchargesPage(
        surcharges=map_surcharges_to_page_items(surcharges),
        is_end_of_list_reached=is_end_of_list_reached,
    )


def map_penalties_to_page_items(
        penalties: Iterable[Penalty],
        photos: Iterable[PenaltyPhoto],
) -> list[PenaltiesPageItem]:
    penalty_id_photo_urls = defaultdict(list)
    for photo in photos:
        penalty_id_photo_urls[photo.penalty_id].append(photo.photo_url)

    return [
        PenaltiesPageItem(
            id=penalty.id,
            staff_id=penalty.shift.staff.id,
            staff_full_name=penalty.shift.staff.full_name,
            shift_id=penalty.shift_id,
            shift_date=penalty.shift.date,
            consequence=penalty.consequence,
            reason=penalty.reason,
            amount=penalty.amount,
            photo_urls=penalty_id_photo_urls[penalty.id],
            created_at=penalty.created_at,
        )
        for penalty in penalties
    ]


def get_penalties_page(
        *,
        staff_ids: Iterable[int] | None = None,
        limit: int,
        offset: int,
) -> PenaltiesPage:
    penalties = (
        Penalty.objects
        .select_related('shift', 'shift__staff')
        .order_by('-created_at')
        .only(
            'id',
            'shift__staff__id',
            'shift__staff__full_name',
            'shift_id',
            'shift__date',
            'consequence',
            'reason',
            'amount',
            'created_at',
        )
    )
    if staff_ids is not None:
        penalties = penalties.filter(shift__staff_id__in=staff_ids)
    penalties = penalties[offset: offset + limit + 1]

    is_end_of_list_reached = len(penalties) <= limit
    penalties = penalties[:limit]

    penalty_ids = [penalty.id for penalty in penalties]
    photos = PenaltyPhoto.objects.filter(penalty_id__in=penalty_ids)

    return PenaltiesPage(
        penalties=map_penalties_to_page_items(
            penalties=penalties,
            photos=photos,
        ),
        is_end_of_list_reached=is_end_of_list_reached,
    )
