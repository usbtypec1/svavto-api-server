import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import (
    ShiftCreateOutputSerializer,
    ShiftExtraCreateInputSerializer,
)
from shifts.services.shifts import create_extra_shift
from staff.selectors import get_staff_by_id
from staff.services import update_last_activity_time


class ShiftExtraCreateApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = ShiftExtraCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        staff_id: int = serialized_data['staff_id']
        dates: list[datetime.date] = serialized_data['dates']

        staff = get_staff_by_id(staff_id)
        update_last_activity_time(staff_id=staff_id)

        shifts_create_result = create_extra_shift(staff=staff, dates=dates)

        serializer = ShiftCreateOutputSerializer(shifts_create_result)
        return Response(serializer.data, status.HTTP_201_CREATED)
