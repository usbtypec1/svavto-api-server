import datetime
from dataclasses import dataclass
from functools import lru_cache

from bonuses.models import BonusSettings
from shifts.models import Shift


@dataclass(frozen=True, slots=True, kw_only=True)
class BonusAmountComputeInteractor:
    shift: Shift

    @lru_cache
    def get_bonus_settings(self):
        return BonusSettings.objects.first()

    def get_shift_transferred_cars_count(self) -> int:
        return self.shift.cartowash_set.count()

    def is_enough_cars(self) -> bool:
        min_cars_count = self.get_bonus_settings().min_cars_count
        transferred_cars_count = self.get_shift_transferred_cars_count()
        return transferred_cars_count >= min_cars_count

    def is_weekend(self) -> bool:
        return self.shift.date.isoweekday() in (6, 7)

    def is_staff_excluded(self) -> bool:
        bonus_settings = self.get_bonus_settings()
        return (
            bonus_settings.excluded_staff
            .filter(id=self.shift.staff_id)
            .exists()
        )

    def is_bonus_settings_exists(self) -> bool:
        return self.get_bonus_settings() is not None

    def execute(self) -> int:
        if self.shift.is_test or self.shift.is_extra or not self.is_weekend():
            return 0

        bonus_settings = self.get_bonus_settings()
        if (
                not self.is_bonus_settings_exists()
                or not bonus_settings.is_bonus_enabled
        ):
            return 0

        if not self.is_enough_cars():
            return 0

        if self.is_staff_excluded():
            return 0

        return bonus_settings.bonus_amount
