from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import (
    DryCleaningRequestCreateInputSerializer,
    DryCleaningRequestListInputSerializer,
    DryCleaningRequestSerializer,
)
from shifts.services import (
    DryCleaningRequestCreateInteractor,
    DryCleaningRequestListInteractor,
)


class DryCleaningRequestListCreateApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = DryCleaningRequestListInputSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)
        shift_ids: list[int] | None = serializer.validated_data["shift_ids"]
        statuses: list[int] | None = serializer.validated_data["statuses"]

        dry_cleaning_requests = DryCleaningRequestListInteractor(
            shift_ids=shift_ids,
            statuses=statuses,
        ).execute()

        serializer = DryCleaningRequestSerializer(
            dry_cleaning_requests,
            many=True,
        )
        return Response({"dry_cleaning_requests": serializer.data})

    def post(self, request: Request) -> Response:
        serializer = DryCleaningRequestCreateInputSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        shift_id: int = serializer.validated_data["shift_id"]
        car_number: str = serializer.validated_data["car_number"]
        photo_file_ids: list[str] = serializer.validated_data["photo_file_ids"]
        services: list[dict] = serializer.validated_data["services"]

        dry_cleaning_request = DryCleaningRequestCreateInteractor(
            shift_id=shift_id,
            car_number=car_number,
            photo_file_ids=photo_file_ids,
            services=services,
        ).execute()

        serializer = DryCleaningRequestSerializer(dry_cleaning_request)
        return Response(serializer.data, status.HTTP_201_CREATED)
