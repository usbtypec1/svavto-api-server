import datetime

from bonuses.models import BonusSettings
from shifts.models import Shift


def is_weekend(date: datetime.date) -> bool:
    return date.isoweekday() in (6, 7)


def get_bonus_amount(shift: Shift) -> int:
    if shift.is_test or shift.is_extra or is_weekend(shift.date):
        return 0

    bonus_settings = BonusSettings.objects.first()
    if bonus_settings is None or not bonus_settings.is_bonus_enabled:
        return 0

    if shift.cartowash_set.count() < bonus_settings.min_cars_count:
        return 0

    if bonus_settings.excluded_staff.filter(id=shift.staff_id).exists():
        return 0

    return bonus_settings.bonus_amount
