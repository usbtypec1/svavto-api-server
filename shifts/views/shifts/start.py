from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.services import ensure_car_wash_exists
from shifts.models import Shift
from shifts.services import start_shift
from staff.services import update_last_activity_time

__all__ = ('ShiftStartApi',)


class ShiftStartInputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()
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

        shift_id: int = serialized_data['shift_id']
        car_wash_id: int = serialized_data['car_wash_id']

        ensure_car_wash_exists(car_wash_id)
        shift = start_shift(
            shift_id=shift_id,
            car_wash_id=car_wash_id,
        )
        update_last_activity_time(staff_id=shift.staff_id)

        serializer = ShiftStartOutputSerializer(shift)
        return Response(serializer.data)
