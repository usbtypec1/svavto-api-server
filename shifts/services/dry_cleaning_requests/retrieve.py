import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from shifts.exceptions import DryCleaningRequestNotFoundError
from shifts.models.dry_cleaning_requests import (
    DryCleaningRequest,
    DryCleaningRequestPhoto,
    DryCleaningRequestService,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestServiceDto:
    id: UUID
    name: str
    count: int
    is_countable: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestRetrieveResponseDto:
    id: int
    shift_id: int
    car_number: str
    photo_urls: list[str]
    services: Iterable[DryCleaningRequestServiceDto]
    status: int
    response_comment: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestRetrieveByIdInteractor:
    dry_cleaning_request_id: int

    def execute(self) -> DryCleaningRequestRetrieveResponseDto:
        try:
            dry_cleaning_request = (
                DryCleaningRequest.objects
                .prefetch_related('photos')
                .get(id=self.dry_cleaning_request_id)
            )
        except DryCleaningRequest.DoesNotExist:
            raise DryCleaningRequestNotFoundError

        services = (
            DryCleaningRequestService.objects
            .filter(request=dry_cleaning_request)
            .select_related('service')
        )
        photos = (
            DryCleaningRequestPhoto.objects
            .filter(request=dry_cleaning_request)
        )
        return DryCleaningRequestRetrieveResponseDto(
            id=dry_cleaning_request.id,
            shift_id=dry_cleaning_request.shift_id,
            car_number=dry_cleaning_request.car_number,
            photo_urls=[photo.url for photo in photos],
            services=[
                DryCleaningRequestServiceDto(
                    id=service.service.id,
                    name=service.service.name,
                    count=service.count,
                    is_countable=service.service.is_countable,
                )
                for service in services
            ],
            status=dry_cleaning_request.status,
            response_comment=dry_cleaning_request.response_comment,
            created_at=dry_cleaning_request.created_at,
            updated_at=dry_cleaning_request.updated_at,
        )
