import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.serializers import (
    CarTransporterPenaltyCreateInputSerializer,
    PenaltyCreateOutputSerializer,
    PenaltyListInputSerializer,
    PenaltyListOutputSerializer,
)
from economics.use_cases import (
    CarTransporterPenaltyCreateUseCase,
    CarTransporterPenaltyDeleteUseCase,
    CarTransporterPenaltyListUseCase,
)


class CarTransporterPenaltyListCreateApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = PenaltyListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.validated_data

        staff_ids: list[int] | None = serialized_data["staff_ids"]
        limit: int = serialized_data["limit"]
        offset: int = serialized_data["offset"]

        penalties_page = CarTransporterPenaltyListUseCase(
            staff_ids=staff_ids,
            limit=limit,
            offset=offset,
        ).execute()

        serializer = PenaltyListOutputSerializer(penalties_page)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = CarTransporterPenaltyCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.validated_data

        staff_id: int = serialized_data["staff_id"]
        date: datetime.date = serialized_data["date"]
        reason: str = serialized_data["reason"]
        amount: int | None = serialized_data["amount"]
        photo_urls: list[str] = serialized_data["photo_urls"]

        penalty = CarTransporterPenaltyCreateUseCase(
            staff_id=staff_id,
            date=date,
            reason=reason,
            amount=amount,
            photo_urls=photo_urls,
        ).execute()

        serializer = PenaltyCreateOutputSerializer(penalty)
        return Response(serializer.data, status.HTTP_201_CREATED)


class CarTransporterPenaltyDeleteApi(APIView):

    def delete(self, request: Request, penalty_id: int) -> Response:
        CarTransporterPenaltyDeleteUseCase(penalty_id=penalty_id).execute()
        return Response(status=status.HTTP_204_NO_CONTENT)
