from dataclasses import dataclass
from enum import StrEnum, auto

from economics.exceptions import InvalidPenaltyConsequenceError
from economics.models import Penalty


class PenaltyReason(StrEnum):
    NOT_SHOWING_UP = auto()
    EARLY_LEAVE = auto()
    LATE_REPORT = auto()


@dataclass(frozen=True, slots=True)
class PenaltyAmountAndConsequence:
    amount: int
    consequence: str | None


def compute_penalty_amount(
    *,
    staff_id: int,
    reason: str,
) -> PenaltyAmountAndConsequence:
    if reason == PenaltyReason.EARLY_LEAVE:
        return PenaltyAmountAndConsequence(amount=1000, consequence=None)

    penalties_count = Penalty.objects.filter(
        staff_id=staff_id,
        reason=reason,
    ).count()

    if reason == PenaltyReason.LATE_REPORT:
        if penalties_count == 0:
            amount = 0
            consequence = Penalty.Consequence.WARN
        elif penalties_count == 1:
            amount = 100
            consequence = None
        elif penalties_count == 2:
            amount = 300
            consequence = None
        else:
            amount = 300
            consequence = None
        return PenaltyAmountAndConsequence(
            amount=amount,
            consequence=consequence,
        )
    elif reason == PenaltyReason.NOT_SHOWING_UP:
        if penalties_count == 0:
            amount = 500
            consequence = None
        elif penalties_count == 1:
            amount = 1000
            consequence = None
        elif penalties_count == 2:
            amount = 1000
            consequence = Penalty.Consequence.DISMISSAL
        else:
            amount = 0
            consequence = Penalty.Consequence.DISMISSAL
        return PenaltyAmountAndConsequence(
            amount=amount,
            consequence=consequence,
        )
    raise InvalidPenaltyConsequenceError


def create_penalty(
    *,
    staff_id: int,
    reason: str,
    amount: int | None,
) -> Penalty:
    consequence: str | None = None
    if amount is None:
        penalty_amount_and_consequence = compute_penalty_amount(
            staff_id=staff_id,
            reason=reason,
        )
        amount = penalty_amount_and_consequence.amount
        consequence = penalty_amount_and_consequence.consequence

    return Penalty.objects.create(
        staff_id=staff_id,
        reason=reason,
        amount=amount,
        consequence=consequence,
    )
