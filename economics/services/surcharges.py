from economics.models import Surcharge

__all__ = ('create_surcharge',)


def create_surcharge(
        *,
        shift_id: int,
        reason: str,
        amount: int,
) -> Surcharge:
    """
    Give surcharge to staff member.

    Keyword Args:
        shift_id: shift surcharge is related to.
        reason: reason for surcharge.
        amount: amount of surcharge.

    Returns:
        Surcharge: created surcharge.
    """
    surcharge = Surcharge(
        shift_id=shift_id,
        reason=reason,
        amount=amount,
    )
    surcharge.full_clean()
    surcharge.save()
    return surcharge
