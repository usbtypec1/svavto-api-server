import datetime
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from shifts.models.dry_cleaning_requests import (
    DryCleaningRequest,
    DryCleaningRequestService,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestServiceDto:
    id: UUID
    name: str
    count: int
    is_countable: bool


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


def get_services_grouped_by_request_id(
        requests: Iterable[DryCleaningRequest],
) -> dict[int, list[DryCleaningRequestService]]:
    services = (
        DryCleaningRequestService.objects
        .select_related('service')
        .filter(request__in=requests)
    )
    services_grouped_by_request_id = defaultdict(list)
    for service in services:
        services_grouped_by_request_id[service.request_id].append(service)
    return services_grouped_by_request_id


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestListInteractor:
    shift_ids: Iterable[int] | None = None

    def execute(self) -> list[DryCleaningRequestListItemDto]:
        requests = DryCleaningRequest.objects.prefetch_related('photos')
        request_id_to_services = get_services_grouped_by_request_id(requests)

        if self.shift_ids is not None:
            requests = requests.filter(shift_id__in=self.shift_ids)

        result: list[DryCleaningRequestListItemDto] = []
        for request in requests:
            services = request_id_to_services.get(request.id, [])
            file_ids = [photo.file_id for photo in request.photos.all()]
            services = [
                DryCleaningRequestServiceDto(
                    id=service.service_id,
                    name=service.service.name,
                    count=service.count,
                    is_countable=service.service.is_countable,
                )
                for service in services
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
