from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.models import Penalty
from economics.serializers import (
    PenaltyCreateInputSerializer,
    PenaltyCreateOutputSerializer,
    PenaltyListInputSerializer,
    PenaltyListOutputSerializer,
)
from economics.services.penalties import create_penalty

__all__ = ('PenaltyListCreateApi',)


class PenaltyListCreateApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = PenaltyListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        staff_ids: list[int] | None = serialized_data['staff_ids']
        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

        penalties = Penalty.objects.order_by('-created_at')

        if staff_ids is not None:
            penalties = penalties.filter(staff_id__in=staff_ids)

        penalties = penalties[offset:offset + limit + 1]
        is_end_of_list_reached = len(penalties) <= limit
        penalties = penalties[:limit]

        serializer = PenaltyListOutputSerializer(penalties, many=True)
        return Response({
            'penalties': serializer.data,
            'is_end_of_list_reached': is_end_of_list_reached,
        })

    def post(self, request: Request) -> Response:
        serializer = PenaltyCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        staff_id: int = serialized_data['staff_id']
        reason: str = serialized_data['reason']
        amount: int | None = serialized_data['amount']

        penalty = create_penalty(
            staff_id=staff_id,
            reason=reason,
            amount=amount,
        )

        serializer = PenaltyCreateOutputSerializer(penalty)
        return Response(serializer.data, status.HTTP_201_CREATED)
