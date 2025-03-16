from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.models import Shift
from shifts.services import get_shifts_by_staff_id


__all__ = ("StaffShiftListApi",)


class StaffShiftListInputSerializer(serializers.Serializer):
    month = serializers.IntegerField(default=None, allow_null=True)
    year = serializers.IntegerField(default=None, allow_null=True)


class StaffShiftListOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            "id",
            "date",
            "started_at",
            "finished_at",
            "created_at",
            "is_test",
            "car_wash",
        )
        depth = 1


class StaffShiftListApi(APIView):
    def get(self, request: Request, staff_id: int) -> Response:
        serializer = StaffShiftListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        month: int | None = serialized_data["month"]
        year: int | None = serialized_data["year"]

        shifts = get_shifts_by_staff_id(
            staff_id=staff_id,
            month=month,
            year=year,
        )
        serializer = StaffShiftListOutputSerializer(shifts, many=True)
        return Response({"shifts": serializer.data})
