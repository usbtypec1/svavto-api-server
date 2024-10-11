from dataclasses import dataclass

from performers.exceptions import PerformerNotFoundError
from performers.models import Performer

__all__ = ('get_performer_by_telegram_id', 'get_all_performers')


@dataclass(frozen=True, slots=True)
class PerformerDTO:
    id: int
    telegram_id: int
    full_name: str
    car_sharing_phone_number: str
    console_phone_number: str
    is_banned: bool
    created_at: bool


def get_performer_by_telegram_id(telegram_id: int) -> Performer:
    try:
        return Performer.objects.get(telegram_id=telegram_id)
    except Performer.DoesNotExist:
        raise PerformerNotFoundError


def get_all_performers() -> list[PerformerDTO]:
    performers = (
        Performer.objects
        .order_by('full_name')
        .values(
            'id',
            'telegram_id',
            'full_name',
            'car_sharing_phone_number',
            'console_phone_number',
            'is_banned',
            'created_at'
        )
    )
    return [
        PerformerDTO(
            id=performer['id'],
            telegram_id=performer['telegram_id'],
            full_name=performer['full_name'],
            car_sharing_phone_number=performer['car_sharing_phone_number'],
            console_phone_number=performer['console_phone_number'],
            is_banned=performer['is_banned'],
            created_at=performer['created_at']
        ) for performer in performers
    ]
