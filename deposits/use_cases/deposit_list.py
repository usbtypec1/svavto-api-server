import datetime
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from deposits.services import compute_staff_deposit_return_date
from economics.use_cases import StaffShiftsStatisticsUseCase
from shifts.services.report_periods import ReportPeriod
from staff.selectors import get_staff, StaffItem


@dataclass(frozen=True, slots=True, kw_only=True)
class ReportPeriodStaffDeposit:
    staff_id: int
    road_accident_deposit_amount: float
    fine_deposit_amount: int


@dataclass(frozen=True, slots=True, kw_only=True)
class DepositListItem:
    report_period: ReportPeriod
    staff_deposits_breakdown: list[ReportPeriodStaffDeposit]


@dataclass(frozen=True, slots=True, kw_only=True)
class StaffListItem:
    id: int
    full_name: str
    console_phone_number: str
    car_sharing_phone_number: str
    banned_at: datetime.datetime | None
    deposit_return_at: datetime.datetime | None
    total_fine_deposit_amount: int
    total_road_accident_deposit_amount: int
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class DepositListResponse:
    staff_list: list[StaffListItem]
    deposits: list[DepositListItem]


def merge_staff_list(
        staff: Iterable[StaffItem],
        staff_id_to_total_road_accident_deposit_amount: dict[int, int | float],
        staff_id_to_total_fine_deposit_amount: dict[int, int],
) -> list[StaffListItem]:
    return [
        StaffListItem(
            id=staff_item.id,
            full_name=staff_item.full_name,
            console_phone_number=staff_item.console_phone_number,
            car_sharing_phone_number=(
                staff_item.car_sharing_phone_number
            ),
            banned_at=staff_item.banned_at,
            deposit_return_at=compute_staff_deposit_return_date(
                banned_at=staff_item.banned_at,
            ),
            total_fine_deposit_amount=(
                staff_id_to_total_fine_deposit_amount.get(staff_item.id, 0)
            ),
            total_road_accident_deposit_amount=(
                staff_id_to_total_road_accident_deposit_amount.get(
                    staff_item.id, 0
                )
            ),
            created_at=staff_item.created_at,
        )
        for staff_item in staff
    ]


@dataclass(frozen=True, slots=True, kw_only=True)
class DepositListUseCase:
    from_report_period: ReportPeriod
    to_report_period: ReportPeriod

    def execute(self) -> DepositListResponse:
        current_report_period = self.from_report_period

        staff_list = get_staff()

        staff_id_to_total_road_accident_deposit_amount = defaultdict(int)
        staff_id_to_total_fine_deposit_amount = defaultdict(int)

        deposits: list[DepositListItem] = []

        while current_report_period <= self.to_report_period:
            staff_shifts_statistics = StaffShiftsStatisticsUseCase(
                year=current_report_period.year,
                month=current_report_period.month,
                report_period_number=current_report_period.number,
            ).execute()

            report_period_staff_deposits: list[ReportPeriodStaffDeposit] = []
            for staff in staff_shifts_statistics.staff_list:
                staff_id = staff.staff.id

                road_accident_deposit_amount = (
                    staff.total_statistics.road_accident_deposit_amount
                )
                fine_deposit_amount = (
                    staff.total_statistics.fine_deposit_amount
                )
                report_period_staff_deposits.append(
                    ReportPeriodStaffDeposit(
                        staff_id=staff.staff.id,
                        road_accident_deposit_amount=(
                            road_accident_deposit_amount
                        ),
                        fine_deposit_amount=(
                            staff.total_statistics.fine_deposit_amount
                        ),
                    )
                )
                staff_id_to_total_road_accident_deposit_amount[staff_id] += (
                    road_accident_deposit_amount
                )
                staff_id_to_total_fine_deposit_amount[staff_id] += (
                    fine_deposit_amount
                )

            deposits.append(
                DepositListItem(
                    report_period=current_report_period,
                    staff_deposits_breakdown=report_period_staff_deposits,
                )
            )

            current_report_period = current_report_period.next()

        return DepositListResponse(
            staff_list=merge_staff_list(
                staff=staff_list,
                staff_id_to_total_road_accident_deposit_amount=(
                    staff_id_to_total_road_accident_deposit_amount
                ),
                staff_id_to_total_fine_deposit_amount=(
                    staff_id_to_total_fine_deposit_amount
                ),
            ),
            deposits=deposits,
        )
