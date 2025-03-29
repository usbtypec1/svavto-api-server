from dataclasses import dataclass

from shifts.services.report_periods import ReportPeriod



@dataclass(frozen=True, slots=True, kw_only=True)
class DepositListUseCase:
    from_report_period_year: int
    from_report_period_month: int
    from_report_period_number: int
    to_report_period_year: int
    to_report_period_month: int
    to_report_period_number: int

    def