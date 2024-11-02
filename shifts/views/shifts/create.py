from datetime import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status

from shifts.services.shifts import create_unconfirmed_shifts

__all__ = ('ShiftCreateApi',)

from staff.selectors import get_staff_by_id


class ShiftCreateInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    dates = serializers.ListField(child=serializers.DateField())


class ShiftCreateApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = ShiftCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        staff_id: int = serialized_data['staff_id']
        dates: list[datetime.date] = serialized_data['dates']

        staff = get_staff_by_id(staff_id)
        create_unconfirmed_shifts(staff=staff, dates=dates)

        response_data = {
            'staff_id': staff.id,
            'staff_full_name': staff.full_name,
            'dates': dates,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
