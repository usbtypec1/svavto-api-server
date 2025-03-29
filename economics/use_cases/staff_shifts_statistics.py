from collections.abc import Iterable
from dataclasses import dataclass

from deposits.services import get_fine_deposit_exceptions_for_report_period
from economics.selectors import (
    get_car_transporters_penalties_for_period,
    get_car_transporters_surcharges_for_period,
)
from economics.services.reports.staff_shifts_statistics import (
    get_cars_to_wash_statistics, group_shifts_statistics_by_staff,
    merge_shifts_statistics_and_penalties_and_surcharges,
    StaffShiftsStatisticsResponse,
)
from shifts.services.report_periods import get_report_period_by_number
from staff.selectors import get_staff


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffShiftsStatisticsUseCase:
    year: int
    month: int
    report_period_number: int
    staff_ids: Iterable[int] | None = None

    def execute(self) -> StaffShiftsStatisticsResponse:
        period = get_report_period_by_number(
            year=self.year,
            month=self.month,
            report_period_number=self.report_period_number,
        )
        staff_list = get_staff(staff_ids=self.staff_ids)
        penalties = get_car_transporters_penalties_for_period(
            staff_ids=self.staff_ids,
            from_date=period.from_date,
            to_date=period.to_date,
        )
        surcharges = get_car_transporters_surcharges_for_period(
            staff_ids=self.staff_ids,
            from_date=period.from_date,
            to_date=period.to_date,
        )
        shifts_statistics = get_cars_to_wash_statistics(
            staff_ids=self.staff_ids,
            from_date=period.from_date,
            to_date=period.to_date,
        )
        staff_shifts_statistics = group_shifts_statistics_by_staff(
            shifts_statistics=shifts_statistics,
        )
        fine_deposit_exceptions = (
            get_fine_deposit_exceptions_for_report_period(
                year=self.year,
                month=self.month,
                report_period_number=self.report_period_number,
            )
        )
        staff_statistics = [
            merge_shifts_statistics_and_penalties_and_surcharges(
                staff=staff,
                penalties=penalties,
                surcharges=surcharges,
                staff_shifts_statistics=staff_shifts_statistics,
                fine_deposit_exceptions=fine_deposit_exceptions,
            )
            for staff in staff_list
        ]
        return StaffShiftsStatisticsResponse(
            staff_list=staff_statistics,
            report_period=period,
        )
