from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.models import StaffAvailableDate
from staff.selectors import get_staff_by_id
from staff.services import update_staff, update_staff_shift_schedule

__all__ = (
    'PerformerRetrieveUpdateApi',
    'StaffUpdateAvailableDatesApi',
)


class StaffAvailableDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAvailableDate
        fields = ['month', 'year']


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
        available_dates = StaffAvailableDateSerializer(
            many=True,
            source='staffavailabledate_set',
        )

    def get(self, request: Request, staff_id: int) -> Response:
        staff = get_staff_by_id(staff_id)
        serializer = self.OutputSerializer(staff)
        return Response(serializer.data)

    def put(self, request: Request, staff_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data
        is_banned: bool = serialized_data['is_banned']
        update_staff(staff_id=staff_id, is_banned=is_banned)
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffUpdateAvailableDatesApi(APIView):
    class InputSerializer(serializers.Serializer):
        class MonthAndYearSerializer(serializers.Serializer):
            month = serializers.IntegerField(min_value=1, max_value=12)
            year = serializers.IntegerField(min_value=1, max_value=9999)

        dates = MonthAndYearSerializer(many=True)

    def patch(self, request: Request, staff_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data
        update_staff_shift_schedule(
            staff_id=staff_id,
            years_and_months=serialized_data['dates']
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
