import datetime

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.services import ensure_car_wash_exists
from shifts.models import Shift
from shifts.services.shifts import start_shift
from staff.selectors import ensure_staff_exists

__all__ = ('ShiftStartApi',)


class ShiftStartInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    date = serializers.DateField()
    car_wash_id = serializers.IntegerField()


class ShiftStartOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ('id', 'date', 'car_wash', 'staff')
        depth = 1


class ShiftStartApi(APIView):
    """API endpoint is used by staff to start their shift."""

    def post(self, request: Request) -> Response:
        serializer = ShiftStartInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        staff_id: int = serialized_data['staff_id']
        date: datetime.date = serialized_data['date']
        car_wash_id: int = serialized_data['car_wash_id']

        ensure_staff_exists(staff_id)
        ensure_car_wash_exists(car_wash_id)
        shift = start_shift(
            staff_id=staff_id,
            date=date,
            car_wash_id=car_wash_id,
        )

        serializer = ShiftStartOutputSerializer(shift)
        return Response(serializer.data)
