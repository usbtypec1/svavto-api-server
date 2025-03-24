import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from economics.models import CarTransporterSurcharge


@dataclass(frozen=True, slots=True, kw_only=True)
class SurchargesPageItem:
    id: int
    staff_id: int
    staff_full_name: str
    date: datetime.date
    reason: str
    amount: int
    created_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SurchargesPage:
    surcharges: list[SurchargesPageItem]
    is_end_of_list_reached: bool


def map_surcharges_to_page_items(
        surcharges: Iterable[CarTransporterSurcharge],
) -> list[SurchargesPageItem]:
    return [
        SurchargesPageItem(
            id=surcharge.id,
            staff_id=surcharge.staff.id,
            staff_full_name=surcharge.staff.full_name,
            date=surcharge.date,
            reason=surcharge.reason,
            amount=surcharge.amount,
            created_at=surcharge.created_at,
        )
        for surcharge in surcharges
    ]


@dataclass(frozen=True, slots=True, kw_only=True)
class CarTransporterSurchargeListUseCase:
    limit: int
    offset: int
    staff_ids: Iterable[int] | None = None

    def execute(self):
        surcharges = (
            CarTransporterSurcharge.objects.select_related("staff")
            .order_by("-created_at")
            .only(
                "id",
                "staff__id",
                "staff__full_name",
                "date",
                "reason",
                "amount",
                "created_at",
            )
        )
        if self.staff_ids is not None:
            surcharges = surcharges.filter(shift__staff_id__in=self.staff_ids)
        surcharges = surcharges[self.offset: self.offset + self.limit + 1]

        is_end_of_list_reached = len(surcharges) <= self.limit
        surcharges = surcharges[:self.limit]

        return SurchargesPage(
            surcharges=map_surcharges_to_page_items(surcharges),
            is_end_of_list_reached=is_end_of_list_reached,
        )
