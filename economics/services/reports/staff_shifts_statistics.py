import datetime
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol, TypeVar

from economics.models import StaffServicePrice
from economics.selectors import (
    StaffPenaltiesOrSurchargesForSpecificShift,
)
from shifts.models import CarToWash, CarToWashAdditionalService, Shift
from shifts.services.report_periods import ReportPeriod
from staff.models import Staff
from staff.selectors import StaffItem


__all__ = (
    "get_shift_dates",
    "get_shifts_dry_cleaning_items",
    "group_by_shift_id",
    "group_by_staff_id",
    "group_shifts_statistics_by_staff",
    "get_cars_to_wash_statistics",
    "map_shift_statistics_with_penalty_and_surcharge",
    "merge_shifts_statistics_and_penalties_and_surcharges",
    "compute_washed_cars_total_cost",
)


class HasShiftDate(Protocol):
    shift_date: datetime.date


HasShiftDateT = TypeVar("HasShiftDateT", bound=HasShiftDate)


def get_shift_dates(items: Iterable[HasShiftDateT]) -> set[datetime.date]:
    return {item.shift_date for item in items}


@dataclass(frozen=True, slots=True, kw_only=True)
class TotalStatistics:
    penalty_amount: int
    surcharge_amount: int
    planned_comfort_cars_washed_count: int
    planned_business_cars_washed_count: int
    planned_vans_washed_count: int
    urgent_cars_washed_count: int
    extra_shifts_count: int
    dry_cleaning_items_count: int
    washed_cars_total_cost: int
    washed_cars_total_count: int
    dirty_revenue: int
    fine_deposit_amount: int

    @property
    def road_accident_deposit_amount(self) -> float:
        return round(self.dirty_revenue * 0.03, 2)

    @property
    def net_revenue(self) -> float:
        return (
                self.dirty_revenue
                - self.fine_deposit_amount
                - self.road_accident_deposit_amount
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftStatistics:
    staff_id: int
    shift_id: int
    shift_date: datetime.date
    washed_cars_total_cost: int
    planned_comfort_cars_washed_count: int
    planned_business_cars_washed_count: int
    planned_vans_washed_count: int
    urgent_cars_washed_count: int
    dry_cleaning_items_count: int
    is_extra_shift: bool

    @property
    def washed_cars_total_count(self) -> int:
        return (
                self.planned_comfort_cars_washed_count
                + self.planned_business_cars_washed_count
                + self.planned_vans_washed_count
                + self.urgent_cars_washed_count
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ShiftDryCleaningItems:
    staff_id: int
    shift_id: int
    items_count: int


@dataclass(frozen=True, slots=True)
class ShiftStatisticsWithPenaltyAndSurcharge(ShiftStatistics):
    penalty_amount: int
    surcharge_amount: int

    @property
    def dirty_revenue(self) -> int:
        return (
                self.washed_cars_total_cost
                + self.surcharge_amount
                - self.penalty_amount
        )

    @property
    def road_accident_deposit_amount(self) -> float:
        return round(self.dirty_revenue * 0.03, 2)


@dataclass(frozen=True, slots=True)
class StaffShiftsStatistics:
    staff: StaffItem
    shifts_statistics: list[ShiftStatisticsWithPenaltyAndSurcharge]
    total_statistics: TotalStatistics


@dataclass(frozen=True, slots=True)
class StaffShiftsStatisticsResponse:
    staff_list: list[StaffShiftsStatistics]
    report_period: ReportPeriod


@dataclass(frozen=True, slots=True)
class ShiftStatisticsGroupedByStaff:
    staff_id: int
    shifts_statistics: list[ShiftStatistics]


def map_shift_statistics_with_penalty_and_surcharge(
        *,
        shift_statistics: ShiftStatistics,
        penalty_amount: int,
        surcharge_amount: int,
) -> ShiftStatisticsWithPenaltyAndSurcharge:
    return ShiftStatisticsWithPenaltyAndSurcharge(
        staff_id=shift_statistics.staff_id,
        shift_id=shift_statistics.shift_id,
        shift_date=shift_statistics.shift_date,
        washed_cars_total_cost=shift_statistics.washed_cars_total_cost,
        planned_comfort_cars_washed_count=shift_statistics
        .planned_comfort_cars_washed_count,
        planned_business_cars_washed_count=shift_statistics
        .planned_business_cars_washed_count,
        planned_vans_washed_count=shift_statistics.planned_vans_washed_count,
        urgent_cars_washed_count=shift_statistics.urgent_cars_washed_count,
        dry_cleaning_items_count=shift_statistics.dry_cleaning_items_count,
        is_extra_shift=shift_statistics.is_extra_shift,
        penalty_amount=penalty_amount,
        surcharge_amount=surcharge_amount,
    )


def compute_fine_deposit_amount(
        staff_id: int,
        shifts_count: int,
        total_dirty_revenue: int,
        fine_deposit_exceptions: Iterable[Staff],
) -> int:
    fine_deposit_exceptions_staff_ids = {
        staff.id for staff in fine_deposit_exceptions
    }
    if staff_id in fine_deposit_exceptions_staff_ids:
        return 0
    any_shift = bool(shifts_count)
    if not any_shift or total_dirty_revenue < 500:
        return 0
    return 500


def merge_shifts_statistics_and_penalties_and_surcharges(
        *,
        staff: StaffItem,
        staff_shifts_statistics: Iterable[ShiftStatisticsGroupedByStaff],
        penalties: Iterable[StaffPenaltiesOrSurchargesForSpecificShift],
        surcharges: Iterable[StaffPenaltiesOrSurchargesForSpecificShift],
        fine_deposit_exceptions: Iterable[Staff],
) -> StaffShiftsStatistics:
    staff_id_to_penalties = {penalty.staff_id: penalty.items for penalty in
                             penalties}
    staff_id_to_surcharges = {
        surcharge.staff_id: surcharge.items for surcharge in surcharges
    }
    staff_id_to_shifts_statistics = {
        item.staff_id: item.shifts_statistics for item in
        staff_shifts_statistics
    }

    penalties = staff_id_to_penalties.get(staff.id, [])
    surcharges = staff_id_to_surcharges.get(staff.id, [])

    shift_date_to_penalty_amount = {
        penalty.shift_date: penalty.total_amount for penalty in penalties
    }
    shift_date_to_surcharge_amount = {
        surcharge.shift_date: surcharge.total_amount for surcharge in
        surcharges
    }

    shifts_statistics = staff_id_to_shifts_statistics.get(staff.id, [])

    result: list[ShiftStatisticsWithPenaltyAndSurcharge] = []

    total_penalty_amount: int = 0
    total_surcharge_amount: int = 0
    total_planned_comfort_cars_washed_count: int = 0
    total_planned_business_cars_washed_count: int = 0
    total_planned_vans_washed_count: int = 0
    total_urgent_cars_washed_count: int = 0
    total_extra_shifts_count: int = 0
    total_washed_cars_total_cost: int = 0
    total_washed_cars_total_count: int = 0
    total_dirty_revenue: int = 0
    total_dry_cleaning_items_count: int = 0

    for shift_statistics in shifts_statistics:
        penalty_amount = shift_date_to_penalty_amount.get(
            shift_statistics.shift_date,
            0,
        )
        surcharge_amount = shift_date_to_surcharge_amount.get(
            shift_statistics.shift_date,
            0,
        )

        shift_statistics = map_shift_statistics_with_penalty_and_surcharge(
            shift_statistics=shift_statistics,
            surcharge_amount=surcharge_amount,
            penalty_amount=penalty_amount,
        )
        result.append(shift_statistics)
        total_penalty_amount += penalty_amount
        total_surcharge_amount += surcharge_amount
        total_planned_comfort_cars_washed_count += (
            shift_statistics.planned_comfort_cars_washed_count
        )
        total_planned_business_cars_washed_count += (
            shift_statistics.planned_business_cars_washed_count
        )
        total_planned_vans_washed_count += (
            shift_statistics.planned_vans_washed_count
        )
        total_urgent_cars_washed_count += (
            shift_statistics.urgent_cars_washed_count
        )
        total_extra_shifts_count += shift_statistics.is_extra_shift
        total_washed_cars_total_cost += shift_statistics.washed_cars_total_cost
        total_washed_cars_total_count += (
            shift_statistics.washed_cars_total_count
        )
        total_dirty_revenue += shift_statistics.dirty_revenue
        total_dry_cleaning_items_count += (
            shift_statistics.dry_cleaning_items_count
        )
    fine_deposit_amount = compute_fine_deposit_amount(
        shifts_count=len(shifts_statistics),
        total_dirty_revenue=total_dirty_revenue,
        fine_deposit_exceptions=fine_deposit_exceptions,
        staff_id=staff.id,
    )

    total_statistics = TotalStatistics(
        penalty_amount=total_penalty_amount,
        surcharge_amount=total_surcharge_amount,
        planned_comfort_cars_washed_count
        =total_planned_comfort_cars_washed_count,
        planned_business_cars_washed_count
        =total_planned_business_cars_washed_count,
        planned_vans_washed_count=total_planned_vans_washed_count,
        urgent_cars_washed_count=total_urgent_cars_washed_count,
        extra_shifts_count=total_extra_shifts_count,
        dry_cleaning_items_count=total_dry_cleaning_items_count,
        washed_cars_total_cost=total_washed_cars_total_cost,
        washed_cars_total_count=total_washed_cars_total_count,
        dirty_revenue=total_dirty_revenue,
        fine_deposit_amount=fine_deposit_amount,
    )

    return StaffShiftsStatistics(
        staff=staff,
        shifts_statistics=result,
        total_statistics=total_statistics,
    )


class StaffServicePricesSet:

    def __init__(self, staff_service_prices: Iterable[StaffServicePrice]):
        self.__service_type_to_price = {
            service_price.service: service_price.price
            for service_price in staff_service_prices
        }

    @property
    def extra_shift_planned_car_transfer_price(self) -> int:
        return self.__service_type_to_price[
            StaffServicePrice.ServiceType.CAR_TRANSPORTER_EXTRA_SHIFT
        ]

    @property
    def urgent_car_transfer_price(self) -> int:
        return self.__service_type_to_price[
            StaffServicePrice.ServiceType.URGENT_CAR_WASH
        ]

    @property
    def dry_cleaning_item_price(self) -> int:
        return self.__service_type_to_price[
            StaffServicePrice.ServiceType.ITEM_DRY_CLEAN
        ]

    @property
    def under_plan_planned_car_transfer_price(self) -> int:
        return self.__service_type_to_price[
            StaffServicePrice.ServiceType.UNDER_PLAN_PLANNED_CAR_TRANSFER
        ]


def compute_washed_cars_total_cost(
        *,
        total_cost: int,
        comfort_cars_count: int,
        business_cars_count: int,
        vans_count: int,
        urgent_cars_count: int,
        is_extra_shift: int,
        dry_cleaning_items_count: int,
        prices: StaffServicePricesSet,
        transferred_cars_threshold: int,
) -> int:
    """
    Compute total price of car transfer on the shift.

    Keyword Args:
        total_cost: preliminary total cost by standard rates.
        comfort_cars_count: comfort class cars count (part of planned cars).
        business_cars_count: business class cars count (part of planned cars)
        vans_count: vans count (part of planned cars).
        urgent_cars_count: urgent cars count.
        is_extra_shift: flag of extra shift.
        dry_cleaning_items_count: dry cleaning items count.
        transferred_cars_threshold: min number of cars that must be
                                    transferred during the shift.

    Returns:
        Total price of car transfer on the shift.
    """
    planned_cars_count = (
            comfort_cars_count
            + business_cars_count
            + vans_count
    )

    dry_cleaning_cost = (
            prices.dry_cleaning_item_price
            * dry_cleaning_items_count
    )
    if is_extra_shift:
        planned_cars_transfer_cost = (
                prices.extra_shift_planned_car_transfer_price
                * planned_cars_count
        )
        urgent_cars_transfer_cost = (
                prices.urgent_car_transfer_price * urgent_cars_count
        )
        car_transfer_cost = (
                planned_cars_transfer_cost +
                urgent_cars_transfer_cost
        )
        return dry_cleaning_cost + car_transfer_cost

    total_cars_count = planned_cars_count + urgent_cars_count

    if total_cars_count < transferred_cars_threshold:
        planned_cars_transfer_cost = (
                prices.under_plan_planned_car_transfer_price
                * planned_cars_count
        )
        urgent_cars_transfer_cost = (
                prices.urgent_car_transfer_price * urgent_cars_count
        )
        car_transfer_cost = (
                planned_cars_transfer_cost
                + urgent_cars_transfer_cost
        )
        return dry_cleaning_cost + car_transfer_cost

    return total_cost + dry_cleaning_cost


T = TypeVar("T")


def group_by_shift_id(items: Iterable[T]) -> dict[int, list[T]]:
    result: dict[int, list[T]] = defaultdict(list)
    for item in items:
        result[item.shift_id].append(item)
    return dict(result)


def group_by_staff_id(items: Iterable[T]) -> dict[int, list[T]]:
    result: dict[int, list[T]] = defaultdict(list)
    for item in items:
        result[item.staff_id].append(item)
    return dict(result)


def get_shifts_dry_cleaning_items(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
        staff_ids: Iterable[int] | None = None,
) -> list[ShiftDryCleaningItems]:
    """Get dry cleaning items count by shifts of staff.

    Keyword Args:
        from_date: period start date.
        to_date: period end date.
        staff_ids: staff ids to filter by. If None, all staff will be included.

    Returns:
        list of ShiftDryCleaningItems.
    """
    shifts_dry_cleaning_items = (
        CarToWashAdditionalService.objects.select_related(
            'car__shift'
        ).filter(
            car__shift__date__range=(from_date, to_date),
            service__is_dry_cleaning=True,
        ))
    if staff_ids is not None:
        shifts_dry_cleaning_items = shifts_dry_cleaning_items.filter(
            car__shift__staff_id__in=staff_ids
        )

    shift_id_and_staff_id_to_items_count = defaultdict(int)

    for additional_service in shifts_dry_cleaning_items:
        key = (
            additional_service.car.shift_id,
            additional_service.car.shift.staff_id,
        )
        shift_id_and_staff_id_to_items_count[key] += additional_service.count
    return [
        ShiftDryCleaningItems(
            staff_id=staff_id,
            shift_id=shift_id,
            items_count=items_count,
        )
        for (
            shift_id,
            staff_id,
        ), items_count in shift_id_and_staff_id_to_items_count.items()
    ]


def get_cars_to_wash_statistics(
        *,
        from_date: datetime.date,
        to_date: datetime.date,
        staff_ids: Iterable[int] | None = None,
) -> list[ShiftStatistics]:
    prices = StaffServicePricesSet(StaffServicePrice.objects.all())

    cars_to_wash = CarToWash.objects.filter(
        shift__date__range=(from_date, to_date),
    )
    if staff_ids is not None:
        cars_to_wash = cars_to_wash.filter(shift__staff_id__in=staff_ids)
    shift_id_to_cars: dict[int, list[CarToWash]] = group_by_shift_id(
        cars_to_wash
    )

    shifts = Shift.objects.filter(date__range=(from_date, to_date))
    if staff_ids is not None:
        shifts = shifts.filter(staff_id__in=staff_ids)

    shifts_dry_cleaning_items = get_shifts_dry_cleaning_items(
        from_date=from_date,
        to_date=to_date,
        staff_ids=staff_ids,
    )
    shift_id_and_staff_id_to_dry_cleaning_items_count = {
        (
            shift_dry_cleaning_items.shift_id,
            shift_dry_cleaning_items.staff_id,
        ): shift_dry_cleaning_items.items_count
        for shift_dry_cleaning_items in shifts_dry_cleaning_items
    }

    shifts_statistics: list[ShiftStatistics] = []

    for shift in shifts:
        shift_cars = shift_id_to_cars.get(shift.id, [])
        key: tuple[int, int] = (shift.id, shift.staff_id)
        dry_cleaning_items_count = (
            shift_id_and_staff_id_to_dry_cleaning_items_count.get(key, 0)
        )

        car_counts = defaultdict(int)
        for car in shift_cars:
            if car.wash_type == CarToWash.WashType.PLANNED:
                car_counts[car.car_class] += 1
            elif car.wash_type == CarToWash.WashType.URGENT:
                car_counts["urgent"] += 1

        comfort_cars_washed_count = car_counts[CarToWash.CarType.COMFORT]
        business_cars_washed_count = car_counts[CarToWash.CarType.BUSINESS]
        vans_washed_count = car_counts[CarToWash.CarType.VAN]
        urgent_cars_washed_count = car_counts["urgent"]

        preliminary_total_cost = sum(car.transfer_price for car in shift_cars)
        washed_cars_total_cost = compute_washed_cars_total_cost(
            total_cost=preliminary_total_cost,
            comfort_cars_count=comfort_cars_washed_count,
            business_cars_count=business_cars_washed_count,
            vans_count=vans_washed_count,
            urgent_cars_count=urgent_cars_washed_count,
            is_extra_shift=shift.is_extra,
            dry_cleaning_items_count=dry_cleaning_items_count,
            prices=prices,
            transferred_cars_threshold=shift.transferred_cars_threshold,
        )

        shift_statistics = ShiftStatistics(
            staff_id=shift.staff_id,
            shift_id=shift.id,
            shift_date=shift.date,
            washed_cars_total_cost=washed_cars_total_cost,
            planned_comfort_cars_washed_count=comfort_cars_washed_count,
            planned_business_cars_washed_count=business_cars_washed_count,
            planned_vans_washed_count=vans_washed_count,
            urgent_cars_washed_count=urgent_cars_washed_count,
            dry_cleaning_items_count=dry_cleaning_items_count,
            is_extra_shift=shift.is_extra,
        )
        shifts_statistics.append(shift_statistics)

    return shifts_statistics


def group_shifts_statistics_by_staff(
        shifts_statistics: Iterable[ShiftStatistics],
) -> list[ShiftStatisticsGroupedByStaff]:
    return [
        ShiftStatisticsGroupedByStaff(
            staff_id=staff_id, shifts_statistics=shifts_statistics
        )
        for staff_id, shifts_statistics in
        group_by_staff_id(shifts_statistics).items()
    ]
