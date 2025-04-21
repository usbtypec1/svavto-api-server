from dataclasses import dataclass

from bonuses.models import BonusSettings


@dataclass(frozen=True, slots=True, kw_only=True)
class BonusesExcludedStaffListUseCase:

    def execute(self) -> list[int]:
        bonus_settings = BonusSettings.get_or_create()
        return [staff.id for staff in bonus_settings.excluded_staff.all()]
