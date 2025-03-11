import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from shifts.models.dry_cleaning_requests import DryCleaningRequest


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestServiceDto:
    id: UUID
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestListItemDto:
    id: int
    shift_id: int
    car_number: str
    photo_file_ids: list[str]
    services: Iterable[DryCleaningRequestServiceDto]
    status: int
    response_comment: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestListInteractor:
    shift_ids: Iterable[int] | None = None

    def execute(self) -> list[DryCleaningRequestListItemDto]:
        requests = DryCleaningRequest.objects.prefetch_related(
            'services', 'photos'
        )
        if self.shift_ids is not None:
            requests = requests.filter(shift_id__in=self.shift_ids)

        result: list[DryCleaningRequestListItemDto] = []
        for request in requests:
            file_ids = [photo.file_id for photo in request.photos.all()]
            services = [
                DryCleaningRequestServiceDto(
                    id=service.service_id,
                    count=service.count
                )
                for service in request.services.all()
            ]
            item = DryCleaningRequestListItemDto(
                id=request.id,
                shift_id=request.shift_id,
                car_number=request.car_number,
                photo_file_ids=file_ids,
                services=services,
                status=request.status,
                response_comment=request.response_comment,
                created_at=request.created_at,
                updated_at=request.updated_at,
            )
            result.append(item)

        return result
