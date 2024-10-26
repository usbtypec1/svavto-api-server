import datetime

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.selectors import get_staff_list_by_shift_date

__all__ = ('ShiftDateStaffListApi',)


class ShiftDateStaffListApi(APIView):
    class InputListSerializer(serializers.Serializer):
        date = serializers.DateField()

    class OutputSerializer(serializers.Serializer):
        shift_id = serializers.IntegerField()
        staff_full_name = serializers.CharField()

    def get(self, request: Request) -> Response:
        serializer = self.InputListSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        date: datetime.date = serialized_data['date']

        staff_list = get_staff_list_by_shift_date(date)
        serializer = self.OutputSerializer(staff_list, many=True)
        return Response({'staff_list': serializer.data})
