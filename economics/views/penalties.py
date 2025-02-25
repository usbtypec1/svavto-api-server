from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.selectors import get_penalties_page
from economics.serializers import (
    PenaltyCreateInputSerializer,
    PenaltyCreateOutputSerializer,
    PenaltyListInputSerializer,
    PenaltyListOutputSerializer,
)
from economics.services.penalties import (
    CarTransporterPenaltyDeleteInteractor,
    create_penalty,
)
from shifts.services.shifts.validators import ensure_shift_exists


__all__ = ('PenaltyListCreateApi', 'CarTransporterPenaltyDeleteApi')


class PenaltyListCreateApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = PenaltyListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.validated_data

        staff_ids: list[int] | None = serialized_data['staff_ids']
        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

        penalties_page = get_penalties_page(
            staff_ids=staff_ids,
            limit=limit,
            offset=offset,
        )

        serializer = PenaltyListOutputSerializer(penalties_page)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PenaltyCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.validated_data

        shift_id: int = serialized_data['shift_id']
        reason: str = serialized_data['reason']
        amount: int | None = serialized_data['amount']
        photo_urls: list[str] = serialized_data['photo_urls']

        ensure_shift_exists(shift_id)
        penalty = create_penalty(
            shift_id=shift_id,
            reason=reason,
            amount=amount,
            photo_urls=photo_urls,
        )

        serializer = PenaltyCreateOutputSerializer(penalty)
        return Response(serializer.data, status.HTTP_201_CREATED)


class CarTransporterPenaltyDeleteApi(APIView):

    def delete(self, request: Request, penalty_id: int) -> Response:
        interactor = CarTransporterPenaltyDeleteInteractor(
            penalty_id=penalty_id,
        )
        interactor.execute()
        return Response(status=status.HTTP_204_NO_CONTENT)
