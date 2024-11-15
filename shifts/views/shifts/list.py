import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.models import Shift
from shifts.serializers import (
    ShiftListInputSerializer,
    ShiftListOutputSerializer,
)

__all__ = ('ShiftListApi',)


class ShiftListApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = ShiftListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        date_from: datetime.date | None = serialized_data['date_from']
        date_to: datetime.date | None = serialized_data['date_to']
        staff_ids: list[int] | None = serialized_data['staff_ids']
        limit: int = serialized_data['limit']
        offset: int = serialized_data['offset']

        shifts = (
            Shift.objects
            .select_related('staff', 'car_wash')
            .order_by('-created_at')
        )

        if date_from is not None:
            shifts = shifts.filter(date__gte=date_from)
        if date_to is not None:
            shifts = shifts.filter(date__lte=date_to)
        if staff_ids is not None:
            shifts = shifts.filter(staff_id__in=staff_ids)

        shifts = shifts[offset:offset + limit + 1]
        is_end_of_list_reached = len(shifts) <= limit
        shifts = shifts[:limit]

        serializer = ShiftListOutputSerializer(shifts, many=True)
        return Response({
            'shifts': serializer.data,
            'is_end_of_list_reached': is_end_of_list_reached
        })
