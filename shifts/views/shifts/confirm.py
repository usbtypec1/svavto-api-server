import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status

from shifts.services.shifts import confirm_shift

__all__ = ('ShiftConfirmApi',)


class ShiftConfirmInputSerializer(serializers.Serializer):
    date = serializers.DateField()
    staff_id = serializers.IntegerField()


class ShiftConfirmApi(APIView):
    def post(self, request: Request) -> Response:
        serializer = ShiftConfirmInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        date: datetime.date = serialized_data['date']
        staff_id: int = serialized_data['staff_id']

        confirm_shift(date=date, staff_id=staff_id)

        return Response(status=status.HTTP_204_NO_CONTENT)
