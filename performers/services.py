from django.db import IntegrityError
from django.utils import timezone

from performers.exceptions import (
    PerformerAlreadyExistsError,
    PerformerNotFoundError,
)
from performers.models import Performer

__all__ = ('create_performer', 'update_performer')


def create_performer(
        *,
        telegram_id: int,
        full_name: str,
        car_sharing_phone_number: str,
        console_phone_number: str,
) -> Performer:
    try:
        return Performer.objects.create(
            telegram_id=telegram_id,
            full_name=full_name,
            car_sharing_phone_number=car_sharing_phone_number,
            console_phone_number=console_phone_number
        )
    except IntegrityError:
        raise PerformerAlreadyExistsError


def update_performer(
        *,
        telegram_id: int,
        is_banned: bool,
) -> None:
    banned_at = timezone.now() if is_banned else None
    is_updated = (
        Performer.objects
        .filter(telegram_id=telegram_id)
        .update(banned_at=banned_at)
    )
    if not is_updated:
        raise PerformerNotFoundError
