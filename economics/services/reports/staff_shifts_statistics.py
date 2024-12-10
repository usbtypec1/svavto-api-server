import datetime
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from django.db.models import Count, Q, Sum

from economics.selectors import (
    PenaltyOrSurchargeAmountAndShiftDate,
    get_penalties_for_period,
    get_surcharges_for_period,
)
from shifts.models import CarToWash, Shift
from staff.selectors import StaffItem, get_staff

__all__ = (
    'merge_staff_statistics',
    'get_staff_shifts_statistics',
    'get_shifts_statistics_grouped_by_staff',
    'get_shift_dates',
    'match_shifts_statistics_penalties_and_surcharges',
)


class HasShiftDate(Protocol):
    shift_date: datetime.date


HasShiftDateT = TypeVar('HasShiftDateT', bound=HasShiftDate)


def get_shift_dates(items: Iterable[HasShiftDateT]) -> set[datetime.date]:
    return {item.shift_date for item in items}


@dataclass(frozen=True, slots=True)
class ShiftStatistics:
    shift_date: datetime.date
    planned_comfort_cars_washed_count: int
    planned_business_cars_washed_count: int
    planned_vans_washed_count: int
    urgent_cars_washed_count: int
    is_extra_shift: bool
    washed_cars_total_cost: int


@dataclass(frozen=True, slots=True)
class ShiftStatisticsWithPenaltyAndSurcharge(ShiftStatistics):
    penalty_amount: int
    surcharge_amount: int


@dataclass(frozen=True, slots=True)
class StaffShiftsStatistics:
    staff: StaffItem
    shifts_statistics: list[ShiftStatisticsWithPenaltyAndSurcharge]


@dataclass(frozen=True, slots=True)
class ShiftStatisticsGroupedByStaff:
    staff_id: int
    shifts_statistics: tuple[ShiftStatistics, ...]


def merge_staff_statistics(
        staff_id: int,
        staff_id_to_penalty_amount: dict[int, int],
        staff_id_to_surcharge_amount: dict[int, int],
        staff_id_to_cars: dict[int, dict],
) -> dict:
    penalty_amount: int = staff_id_to_penalty_amount.get(staff_id, 0)
    surcharge_amount: int = staff_id_to_surcharge_amount.get(staff_id, 0)
    cars_statistics = staff_id_to_cars.get(staff_id, {})
    keys = (
        'planned_comfort_cars_washed_count',
        'planned_business_cars_washed_count',
        'planned_business_cars_washed_count',
        'planned_vans_washed_count',
        'urgent_cars_washed_count',
        'total_cost',
    )
    statistics = {key: cars_statistics.get(key, 0) for key in keys}
    return {
        'staff_id': staff_id,
        'penalty_amount': penalty_amount,
        'surcharge_amount': surcharge_amount,
        'is_extra_shift': cars_statistics.get('is_extra', False),
    } | statistics


def match_shifts_statistics_penalties_and_surcharges(
        penalty_shift_date_to_amount: Mapping[datetime.date, int],
        surcharge_shift_date_to_amount: Mapping[datetime.date, int],
        dates: Iterable[datetime.date],
        shift_date_to_shift_statistics: Mapping[datetime.date, ShiftStatistics],
) -> list[ShiftStatisticsWithPenaltyAndSurcharge]:
    shifts_statistics: list[ShiftStatisticsWithPenaltyAndSurcharge] = []

    for date in dates:
        shift_statistics: ShiftStatistics | None = (
            shift_date_to_shift_statistics.get(date)
        )
        if shift_statistics is None:
            continue

        penalty_amount = penalty_shift_date_to_amount.get(date, 0)
        surcharge_amount = surcharge_shift_date_to_amount.get(date, 0)

        shifts_statistics.append(
            ShiftStatisticsWithPenaltyAndSurcharge(
                shift_date=date,
                penalty_amount=penalty_amount,
                surcharge_amount=surcharge_amount,
                planned_comfort_cars_washed_count=(
                    shift_statistics.planned_comfort_cars_washed_count
                ),
                planned_business_cars_washed_count=(
                    shift_statistics.planned_business_cars_washed_count
                ),
                planned_vans_washed_count=(
                    shift_statistics.planned_vans_washed_count
                ),
                urgent_cars_washed_count=(
                    shift_statistics.urgent_cars_washed_count
                ),
                is_extra_shift=shift_statistics.is_extra_shift,
                washed_cars_total_cost=shift_statistics.washed_cars_total_cost,
            )
        )

    return shifts_statistics


def match_staff_shifts_statistics(
        *,
        staff: StaffItem,
        staff_id_to_penalties: (
                Mapping[int, Iterable[PenaltyOrSurchargeAmountAndShiftDate]]
        ),
        staff_id_to_surcharges: (
                Mapping[int, Iterable[PenaltyOrSurchargeAmountAndShiftDate]]
        ),
        staff_id_to_shifts_statistics: Mapping[int, Iterable[ShiftStatistics]],
) -> StaffShiftsStatistics:
    penalties = staff_id_to_penalties.get(staff.id, [])
    surcharges = staff_id_to_surcharges.get(staff.id, [])
    shifts = staff_id_to_shifts_statistics.get(staff.id, [])

    penalty_shift_date_to_amount = {
        penalty.shift_date: penalty.total_amount
        for penalty in penalties
    }
    surcharge_shift_date_to_amount = {
        surcharge.shift_date: surcharge.total_amount
        for surcharge in surcharges
    }
    shift_date_to_shift_statistics = {
        shift.shift_date: shift
        for shift in shifts
    }

    all_dates = (
            get_shift_dates(shifts)
            | get_shift_dates(penalties)
            | get_shift_dates(surcharges)
    )

    shifts_statistics = (
        match_shifts_statistics_penalties_and_surcharges(
            penalty_shift_date_to_amount=penalty_shift_date_to_amount,
            surcharge_shift_date_to_amount=(
                surcharge_shift_date_to_amount
            ),
            dates=all_dates,
            shift_date_to_shift_statistics=(
                shift_date_to_shift_statistics
            ),
        )
    )

    return StaffShiftsStatistics(
        staff=staff,
        shifts_statistics=shifts_statistics,
    )


def map_shifts_statistics_grouped_by_staff(
        staff_id_to_shifts_statistics: Mapping[int, Iterable[ShiftStatistics]],
) -> list[ShiftStatisticsGroupedByStaff]:
    return [
        ShiftStatisticsGroupedByStaff(
            staff_id=staff_id,
            shifts_statistics=tuple(shifts_statistics),
        )
        for staff_id, shifts_statistics in
        staff_id_to_shifts_statistics.items()
    ]


def map_shift_statistics(
        shift_date: datetime.date,
        is_extra_shift: bool,
        shift_cars_statistics: Mapping[str, int],
) -> ShiftStatistics:
    washed_cars_total_cost = (
        shift_cars_statistics.get('washed_cars_total_cost', 0)
    )
    comfort_cars_count = (
        shift_cars_statistics.get('planned_comfort_cars_washed_count', 0)
    )
    business_cars_count = (
        shift_cars_statistics.get('planned_business_cars_washed_count', 0)
    )
    vans_count = shift_cars_statistics.get('planned_vans_washed_count', 0)
    urgent_cars_count = shift_cars_statistics.get('urgent_cars_washed_count', 0)

    return ShiftStatistics(
        shift_date=shift_date,
        planned_comfort_cars_washed_count=comfort_cars_count,
        planned_business_cars_washed_count=business_cars_count,
        planned_vans_washed_count=vans_count,
        urgent_cars_washed_count=urgent_cars_count,
        is_extra_shift=is_extra_shift,
        washed_cars_total_cost=washed_cars_total_cost,
    )


@dataclass(frozen=True, slots=True)
class ShiftPartial:
    date: datetime.date
    staff_id: int
    is_extra_shift: bool


def group_shifts_statistics_by_staff(
        *,
        all_shifts: Iterable[ShiftPartial],
        shifts_cars_statistics: Iterable[Mapping[str, Any]],
) -> list[ShiftStatisticsGroupedByStaff]:
    staff_id_and_shift_date_and_is_extra_to_statistics = {
        (
            shift_cars_statistics['shift__staff_id'],
            shift_cars_statistics['shift__date'],
            shift_cars_statistics['shift__is_extra'],
        ):
            shift_cars_statistics
        for shift_cars_statistics in shifts_cars_statistics
    }

    staff_id_to_shifts_statistics: dict[int, list[ShiftStatistics]] = (
        defaultdict(list)
    )
    for shift in all_shifts:
        key = (
            shift.staff_id,
            shift.date,
            shift.is_extra_shift,
        )
        shift_cars_statistics = (
            staff_id_and_shift_date_and_is_extra_to_statistics.get(key, {})
        )
        shift_statistics = map_shift_statistics(
            shift_date=shift.date,
            is_extra_shift=shift.is_extra_shift,
            shift_cars_statistics=shift_cars_statistics,
        )
        staff_id_to_shifts_statistics[shift.staff_id].append(shift_statistics)

    return map_shifts_statistics_grouped_by_staff(staff_id_to_shifts_statistics)


def map_partial_shifts(
        shifts: Iterable[Mapping[str, Any]],
) -> list[ShiftPartial]:
    return [
        ShiftPartial(
            date=shift['date'],
            staff_id=shift['staff_id'],
            is_extra_shift=shift['is_extra'],
        )
        for shift in shifts
    ]


def get_cars_to_wash_statistics(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
        staff_ids: Iterable[int] | None = None,
) -> list[dict]:
    filter_params = {
        'shift__date__gte': from_date,
        'shift__date__lte': to_date,
    }
    if staff_ids is not None:
        filter_params['shift__staff_id__in'] = staff_ids
    return (
        CarToWash.objects.select_related('shift')
        .filter(**filter_params)
        .values('shift__date', 'shift__staff_id', 'shift__is_extra')
        .annotate(
            washed_cars_total_cost=Sum('transfer_price', default=0),
            planned_comfort_cars_washed_count=Count(
                'id',
                filter=Q(
                    car_class=CarToWash.CarType.COMFORT,
                    wash_type=CarToWash.WashType.PLANNED,
                ),
            ),
            planned_business_cars_washed_count=Count(
                'id',
                filter=Q(
                    car_class=CarToWash.CarType.BUSINESS,
                    wash_type=CarToWash.WashType.PLANNED,
                ),
            ),
            planned_vans_washed_count=Count(
                'id',
                filter=Q(
                    car_class=CarToWash.CarType.VAN,
                    shift__is_extra=False,
                    wash_type=CarToWash.WashType.PLANNED,
                ),
            ),
            urgent_cars_washed_count=Count(
                'id',
                filter=Q(
                    wash_type=CarToWash.WashType.URGENT,
                    shift__is_extra=False,
                ),
            ),
        )
    )


def get_partial_shifts_within_period(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
        staff_ids: Iterable[int] | None = None,
) -> list[ShiftPartial]:
    shifts = Shift.objects.filter(date__gte=from_date, date__lte=to_date)
    if staff_ids is not None:
        shifts = shifts.filter(staff_id__in=staff_ids)
    shifts = shifts.values('staff_id', 'date', 'is_extra')
    return map_partial_shifts(shifts)


def get_shifts_statistics_grouped_by_staff(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
        staff_ids: Iterable[int] | None = None,
) -> list[ShiftStatisticsGroupedByStaff]:
    all_shifts = get_partial_shifts_within_period(
        from_date=from_date,
        to_date=to_date,
        staff_ids=staff_ids,
    )
    shifts_cars_statistics = get_cars_to_wash_statistics(
        from_date=from_date,
        to_date=to_date,
        staff_ids=staff_ids,
    )
    return group_shifts_statistics_by_staff(
        all_shifts=all_shifts,
        shifts_cars_statistics=shifts_cars_statistics,
    )


def get_staff_shifts_statistics(
        *,
        staff_ids: Iterable[int],
        from_date: datetime.date,
        to_date: datetime.date,
) -> list[StaffShiftsStatistics]:
    staff_list = get_staff(staff_ids=staff_ids)
    penalties = get_penalties_for_period(
        staff_ids=staff_ids,
        from_date=from_date,
        to_date=to_date,
    )
    surcharges = get_surcharges_for_period(
        staff_ids=staff_ids,
        from_date=from_date,
        to_date=to_date,
    )
    shifts_statistics = get_shifts_statistics_grouped_by_staff(
        from_date=from_date,
        to_date=to_date,
        staff_ids=staff_ids,
    )

    staff_id_to_penalties = {
        penalty.staff_id: penalty.items
        for penalty in penalties
    }
    staff_id_to_surcharges = {
        surcharge.staff_id: surcharge.items
        for surcharge in surcharges
    }
    staff_id_to_shifts = {
        item.staff_id: item.shifts_statistics
        for item in shifts_statistics
    }

    return [
        match_staff_shifts_statistics(
            staff=staff,
            staff_id_to_penalties=staff_id_to_penalties,
            staff_id_to_surcharges=staff_id_to_surcharges,
            staff_id_to_shifts_statistics=staff_id_to_shifts,
        )
        for staff in staff_list
    ]
