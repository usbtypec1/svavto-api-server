import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import (
    ShiftCreateInputSerializer,
    ShiftCreateOutputSerializer,
)
from shifts.services import ShiftRegularCreateInteractor
from staff.selectors import get_staff_by_id
from staff.services import update_last_activity_time


class ShiftRegularCreateApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = ShiftCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data: dict = serializer.validated_data

        staff_id: int = validated_data['staff_id']
        dates: list[datetime.date] = validated_data['dates']

        staff = get_staff_by_id(staff_id)
        update_last_activity_time(staff_id=staff_id)

        shifts_create_result = ShiftRegularCreateInteractor(
            staff=staff,
            dates=dates,
        ).execute()

        serializer = ShiftCreateOutputSerializer(shifts_create_result)
        return Response(serializer.data, status.HTTP_201_CREATED)
