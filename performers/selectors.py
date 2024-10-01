from performers.exceptions import PerformerNotFoundError
from performers.models import Performer

__all__ = ('get_performer_by_telegram_id',)


def get_performer_by_telegram_id(telegram_id: int) -> Performer:
    try:
        return Performer.objects.get(telegram_id=telegram_id)
    except Performer.DoesNotExist:
        raise PerformerNotFoundError
