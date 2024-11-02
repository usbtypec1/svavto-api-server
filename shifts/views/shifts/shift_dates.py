from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers

from shifts.models import Shift
from shifts.services.shifts import get_shifts_by_staff_id

__all__ = ('StaffShiftListApi',)


class StaffShiftListInputSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()


class StaffShiftListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            'id',
            'date',
            'confirmed_at',
            'started_at',
            'finished_at',
            'created_at',
            'car_wash',
        )
        depth = 1


class StaffShiftListApi(APIView):

    def get(self, request: Request, staff_id: int) -> Response:
        serializer = StaffShiftListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        month: int = serialized_data['month']
        year: int = serialized_data['year']

        shifts = get_shifts_by_staff_id(
            staff_id=staff_id,
            month=month,
            year=year,
        )
        serializer = StaffShiftListOutputSerializer(shifts, many=True)
        return Response({'shifts': serializer.data})
