import datetime
from dataclasses import dataclass

__all__ = ('ShiftDTO',)


@dataclass(frozen=True, slots=True)
class ShiftDTO:
    id: int
    performer_telegram_id: int
    date: datetime.date
