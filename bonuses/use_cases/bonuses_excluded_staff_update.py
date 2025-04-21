from collections.abc import Iterable
from dataclasses import dataclass

from bonuses.models import BonusSettings
from staff.models import Staff


@dataclass(frozen=True, slots=True, kw_only=True)
class BonusesExcludedStaffUpdateUseCase:
    staff_ids: Iterable[int]

    def execute(self) -> None:
        staff_list = Staff.objects.filter(id__in=self.staff_ids)
        bonus_settings = BonusSettings.get_or_create()
        bonus_settings.excluded_staff.set(staff_list)
