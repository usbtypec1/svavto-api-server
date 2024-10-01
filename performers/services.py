from django.db import IntegrityError

from performers.exceptions import PerformerAlreadyExistsError
from performers.models import Performer

__all__ = ('create_performer',)


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
