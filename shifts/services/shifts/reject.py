from django.utils import timezone

from shifts.models import Shift


__all__ = ("mark_shift_as_rejected_now",)


def mark_shift_as_rejected_now(
    shift_id: int,
) -> bool:
    updated_count = Shift.objects.filter(id=shift_id).update(rejected_at=timezone.now())
    return bool(updated_count)
