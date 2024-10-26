from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.selectors import get_staff_by_id
from staff.services import update_staff, update_staff_shift_schedule

__all__ = (
    'PerformerRetrieveUpdateApi',
    'StaffUpdateShiftScheduleYearAndMonthApi',
)


class PerformerRetrieveUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        is_banned = serializers.BooleanField()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        full_name = serializers.CharField(max_length=100)
        car_sharing_phone_number = serializers.CharField(max_length=16)
        console_phone_number = serializers.CharField(max_length=16)
        created_at = serializers.DateTimeField()
        is_banned = serializers.BooleanField()

    def get(self, request: Request, staff_id: int) -> Response:
        performer = get_staff_by_id(staff_id)
        serializer = self.OutputSerializer(performer)
        return Response(serializer.data)

    def put(self, request: Request, staff_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data
        is_banned: bool = serialized_data['is_banned']
        update_staff(staff_id=staff_id, is_banned=is_banned)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffUpdateShiftScheduleYearAndMonthApi(APIView):
    class InputSerializer(serializers.Serializer):
        year = serializers.IntegerField()
        month = serializers.IntegerField()

    def patch(self, request: Request, staff_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        year: int = serialized_data['year']
        month: int = serialized_data['month']

        update_staff_shift_schedule(
            staff_id=staff_id,
            year=year,
            month=month,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
