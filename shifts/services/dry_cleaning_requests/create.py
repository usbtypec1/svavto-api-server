import datetime
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from django.db import transaction

from shifts.models.dry_cleaning_requests import (
    DryCleaningRequest,
    DryCleaningRequestPhoto,
    DryCleaningRequestService,
)
from shifts.services.shifts.validators import ensure_shift_exists


class HasIdAndCount(TypedDict):
    id: UUID
    count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestServiceDto:
    id: UUID
    name: str
    count: int
    is_countable: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class DryCleaningRequestCreateResponseDto:
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
class DryCleaningRequestCreateInteractor:
    shift_id: int
    car_number: str
    photo_file_ids: Iterable[str]
    services: Iterable[HasIdAndCount]

    @transaction.atomic
    def execute(self) -> DryCleaningRequestCreateResponseDto:
        ensure_shift_exists(self.shift_id)
        dry_cleaning_request = DryCleaningRequest.objects.create(
            shift_id=self.shift_id,
            car_number=self.car_number,
        )
        photos = DryCleaningRequestPhoto.objects.bulk_create(
            DryCleaningRequestPhoto(
                request=dry_cleaning_request,
                file_id=file_id,
            )
            for file_id in self.photo_file_ids
        )
        services = DryCleaningRequestService.objects.bulk_create(
            DryCleaningRequestService(
                request=dry_cleaning_request,
                service_id=service['id'],
                count=service['count'],
            )
            for service in self.services
        )
        return DryCleaningRequestCreateResponseDto(
            id=dry_cleaning_request.id,
            shift_id=dry_cleaning_request.shift_id,
            car_number=dry_cleaning_request.car_number,
            photo_file_ids=[photo.file_id for photo in photos],
            services=[
                DryCleaningRequestServiceDto(
                    id=service.service_id,
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
