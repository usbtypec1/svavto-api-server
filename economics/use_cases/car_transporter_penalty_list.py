import datetime
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from economics.models import CarTransporterPenalty, PenaltyPhoto


@dataclass(frozen=True, slots=True, kw_only=True)
class PenaltiesPageItem:
    id: int
    staff_id: int
    staff_full_name: str
    date: datetime.date
    consequence: str | None
    reason: str
    amount: int
    photo_urls: list[str]
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class PenaltiesPage:
    penalties: list[PenaltiesPageItem]
    is_end_of_list_reached: bool


def map_penalties_to_page_items(
        penalties: Iterable[CarTransporterPenalty],
        photos: Iterable[PenaltyPhoto],
) -> list[PenaltiesPageItem]:
    penalty_id_photo_urls = defaultdict(list)
    for photo in photos:
        penalty_id_photo_urls[photo.penalty_id].append(photo.photo_url)

    return [
        PenaltiesPageItem(
            id=penalty.id,
            staff_id=penalty.staff.id,
            staff_full_name=penalty.staff.full_name,
            date=penalty.date,
            consequence=penalty.consequence,
            reason=penalty.reason,
            amount=penalty.amount,
            photo_urls=penalty_id_photo_urls[penalty.id],
            created_at=penalty.created_at,
        )
        for penalty in penalties
    ]


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterPenaltyListUseCase:
    staff_ids: Iterable[int] | None = None
    limit: int
    offset: int

    def execute(self):
        penalties = (
            CarTransporterPenalty.objects.select_related("staff")
            .order_by("-created_at")
            .only(
                "id",
                "staff__id",
                "staff__full_name",
                "date",
                "consequence",
                "reason",
                "amount",
                "created_at",
            )
        )
        if self.staff_ids is not None:
            penalties = penalties.filter(staff_id__in=self.staff_ids)
        penalties = penalties[self.offset: self.offset + self.limit + 1]

        is_end_of_list_reached = len(penalties) <= self.limit
        penalties = penalties[:self.limit]

        penalty_ids = [penalty.id for penalty in penalties]
        photos = PenaltyPhoto.objects.filter(penalty_id__in=penalty_ids)

        return PenaltiesPage(
            penalties=map_penalties_to_page_items(
                penalties=penalties,
                photos=photos,
            ),
            is_end_of_list_reached=is_end_of_list_reached,
        )
