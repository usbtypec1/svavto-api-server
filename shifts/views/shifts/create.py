from datetime import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import ShiftCreateInputSerializer
from shifts.services.shifts import create_and_start_shifts, create_shifts
from staff.selectors import get_staff_by_id

__all__ = ('ShiftCreateApi',)


class ShiftCreateApi(APIView):
    def post(self, request: Request) -> Response:
        serializer = ShiftCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        staff_id: int = serialized_data['staff_id']
        dates: list[datetime.date] = serialized_data['dates']
        immediate_start: bool = serialized_data['immediate_start']
        car_wash_id: int | None = serialized_data['car_wash_id']
        is_extra: bool = serialized_data['is_extra']

        staff = get_staff_by_id(staff_id)

        if immediate_start:
            create_and_start_shifts(
                staff=staff,
                dates=dates,
                car_wash_id=car_wash_id,
                is_extra=is_extra,
            )
        else:
            create_shifts(
                staff=staff,
                dates=dates,
                is_extra=is_extra,
            )

        response_data = {
            'staff_id': staff.id,
            'staff_full_name': staff.full_name,
            'dates': dates,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
