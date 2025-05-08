import datetime
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from typing import override, Protocol, TypeVar

from economics.models import (
    CarTransporterAndWasherServicePrices,
    CarTransporterServicePrices,
)
from economics.selectors import (
    StaffPenaltiesOrSurchargesForSpecificShift,
)
from shifts.models import (
    CarToWashAdditionalService,
    Shift,
    TransferredCar,
)
from shifts.services.report_periods import ReportPeriod
from staff.models import Staff, StaffType
from staff.selectors import StaffItem


__all__ = (
    "get_shifts_dry_cleaning_items",
    "group_by_shift_id",
    "group_by_staff_id",
    "group_shifts_statistics_by_staff",
    "get_cars_to_wash_statistics",
    "map_shift_statistics_with_penalty_and_surcharge",
    "merge_shifts_statistics_and_penalties_and_surcharges",
)


class HasShiftDate(Protocol):
    shift_date: datetime.date


HasShiftDateT = TypeVar("HasShiftDateT", bound=HasShiftDate)


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


@dataclass(frozen=True, slots=True, kw_only=True)
class DailyShiftStatistics:
    staff_id: int
    date: datetime.date
    washed_cars_total_cost: int
    planned_comfort_cars_washed_count: int
    planned_business_cars_washed_count: int
    planned_vans_washed_count: int
    urgent_cars_washed_count: int
    dry_cleaning_items_count: int
    washed_cars_total_count: int
    is_extra_shift: bool
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
    shifts_statistics: list[DailyShiftStatistics]
    total_statistics: TotalStatistics


@dataclass(frozen=True, slots=True)
class StaffShiftsStatisticsResponse:
    staff_list: list[DailyShiftStatistics]
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
) -> DailyShiftStatistics:
    return DailyShiftStatistics(
        staff_id=shift_statistics.staff_id,
        date=shift_statistics.shift_date,
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
        washed_cars_total_count=shift_statistics.washed_cars_total_count,
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
) -> DailyShiftStatistics:
    date_to_penalty_amount = defaultdict(int)
    for penalty in penalties:
        if penalty.staff_id != staff.id:
            continue
        for item in penalty.items:
            date_to_penalty_amount[item.shift_date] += item.total_amount

    date_to_surcharge_amount = defaultdict(int)
    for surcharge in surcharges:
        if surcharge.staff_id != staff.id:
            continue
        for item in surcharge.items:
            date_to_surcharge_amount[item.shift_date] += item.total_amount

    date_to_shift_statistics = {}
    for staff_shift_statistics in staff_shifts_statistics:
        if staff_shift_statistics.staff_id != staff.id:
            continue
        for shift_statistics in staff_shift_statistics.shifts_statistics:
            date_to_shift_statistics[shift_statistics.shift_date] = (
                shift_statistics
            )

    dates = (
            set(date_to_penalty_amount)
            | set(date_to_surcharge_amount)
            | set(date_to_shift_statistics)
    )

    result: list[DailyShiftStatistics] = []

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

    for date in dates:
        penalty_amount = date_to_penalty_amount.get(date, 0)
        surcharge_amount = date_to_surcharge_amount.get(date, 0)
        shift_statistics = date_to_shift_statistics.get(date)

        if shift_statistics is None:
            shift_statistics = ShiftStatistics(
                staff_id=staff.id,
                shift_id=0,
                shift_date=date,
                washed_cars_total_cost=0,
                planned_comfort_cars_washed_count=0,
                planned_business_cars_washed_count=0,
                planned_vans_washed_count=0,
                urgent_cars_washed_count=0,
                dry_cleaning_items_count=0,
                is_extra_shift=False,
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

    shifts_count = len(date_to_shift_statistics)
    fine_deposit_amount = compute_fine_deposit_amount(
        shifts_count=shifts_count,
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


class HasItemDryCleaningPrice(Protocol):
    item_dry_cleaning: int


@dataclass(kw_only=True)
class ShiftTransferredCarsTotalCostCalculator(ABC):
    cars: Iterable[TransferredCar]
    dry_cleaning_items_count: int
    prices: HasItemDryCleaningPrice

    @cached_property
    def comfort_cars_count(self) -> int:
        return sum(
            car.car_class == TransferredCar.CarType.COMFORT
            for car in self.cars
        )

    @cached_property
    def business_cars_count(self) -> int:
        return sum(
            car.car_class == TransferredCar.CarType.BUSINESS
            for car in self.cars
        )

    @cached_property
    def vans_count(self) -> int:
        return sum(
            car.car_class == TransferredCar.CarType.VAN
            for car in self.cars
        )

    @cached_property
    def urgent_cars_count(self) -> int:
        return sum(
            car.wash_type == TransferredCar.WashType.URGENT
            for car in self.cars
        )

    @cached_property
    def precalculated_total_cost(self) -> int:
        return sum(car.transfer_price for car in self.cars)

    @cached_property
    def planned_cars_count(self) -> int:
        return (
                self.comfort_cars_count
                + self.business_cars_count
                + self.vans_count
        )

    @cached_property
    def total_cars_count(self) -> int:
        return self.planned_cars_count + self.urgent_cars_count

    def calculate_dry_cleaning_cost(self) -> int:
        return self.prices.item_dry_cleaning * self.dry_cleaning_items_count

    @abstractmethod
    def calculate_total_cost(self):
        pass


@dataclass(kw_only=True)
class CarTransporterAndWasherTransferredCarsTotalCostCalculator(
    ShiftTransferredCarsTotalCostCalculator
):
    prices: CarTransporterAndWasherServicePrices

    @override
    def calculate_total_cost(self) -> int:
        return (
                self.precalculated_total_cost +
                self.calculate_dry_cleaning_cost()
        )


@dataclass(kw_only=True)
class CarTransporterTransferredCarsTotalCostCalculator(
    ShiftTransferredCarsTotalCostCalculator
):
    prices: CarTransporterServicePrices
    is_extra_shift: bool
    transferred_cars_min_count: int

    @property
    def is_min_plan_completed(self) -> bool:
        return self.total_cars_count >= self.transferred_cars_min_count

    def calculate_min_plan_not_completed(self) -> int:
        planned_cars_transfer_cost = (
                self.prices.under_plan_planned_car_transfer
                * self.planned_cars_count
        )
        urgent_cars_transfer_cost = (
                self.prices.urgent_car_transfer * self.urgent_cars_count
        )
        car_transfer_cost = (
                planned_cars_transfer_cost
                + urgent_cars_transfer_cost
        )
        return car_transfer_cost + self.calculate_dry_cleaning_cost()

    def calculate_extra_shift(self) -> int:
        planned_cars_transfer_cost = (
                self.prices.extra_shift
                * self.planned_cars_count
        )
        urgent_cars_transfer_cost = (
                self.prices.urgent_car_transfer * self.urgent_cars_count
        )
        car_transfer_cost = (
                planned_cars_transfer_cost + urgent_cars_transfer_cost
        )
        return car_transfer_cost + self.calculate_dry_cleaning_cost()

    def calculate_regular_shift(self) -> int:
        return (
                self.precalculated_total_cost
                + self.calculate_dry_cleaning_cost()
        )

    @override
    def calculate_total_cost(self) -> int:
        if self.is_extra_shift:
            return self.calculate_extra_shift()
        if not self.is_min_plan_completed:
            return self.calculate_min_plan_not_completed()
        return self.calculate_regular_shift()


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
    cars_to_wash = TransferredCar.objects.filter(
        shift__date__range=(from_date, to_date),
    )
    if staff_ids is not None:
        cars_to_wash = cars_to_wash.filter(shift__staff_id__in=staff_ids)
    shift_id_to_cars: dict[int, list[TransferredCar]] = group_by_shift_id(
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

    car_transporter_service_prices = CarTransporterServicePrices.get()
    car_transporter_and_washer_service_prices = (
        CarTransporterAndWasherServicePrices.get()
    )

    for shift in shifts:
        shift_cars = shift_id_to_cars.get(shift.id, [])
        key: tuple[int, int] = (shift.id, shift.staff_id)
        dry_cleaning_items_count = (
            shift_id_and_staff_id_to_dry_cleaning_items_count.get(key, 0)
        )

        if shift.staff.type == StaffType.CAR_TRANSPORTER:
            calculator = CarTransporterTransferredCarsTotalCostCalculator(
                cars=shift_cars,
                dry_cleaning_items_count=dry_cleaning_items_count,
                prices=car_transporter_service_prices,
                is_extra_shift=shift.is_extra,
                transferred_cars_min_count=shift.transferred_cars_threshold,
            )
        else:
            calculator = (
                CarTransporterAndWasherTransferredCarsTotalCostCalculator(
                    cars=shift_cars,
                    dry_cleaning_items_count=dry_cleaning_items_count,
                    prices=car_transporter_and_washer_service_prices,
                )
            )
        shift_statistics = ShiftStatistics(
            staff_id=shift.staff_id,
            shift_id=shift.id,
            shift_date=shift.date,
            washed_cars_total_cost=calculator.calculate_total_cost(),
            planned_comfort_cars_washed_count=calculator.planned_cars_count,
            planned_business_cars_washed_count=calculator.business_cars_count,
            planned_vans_washed_count=calculator.planned_cars_count,
            urgent_cars_washed_count=calculator.urgent_cars_count,
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
