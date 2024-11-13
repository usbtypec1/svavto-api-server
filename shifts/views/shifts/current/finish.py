from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.selectors import get_staff_current_shift
from shifts.services.shifts import finish_shift

__all__ = ('ShiftFinishApi',)


class ShiftFinishInputSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()


class ShiftFinishApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = ShiftFinishInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        staff_id: int = serialized_data['staff_id']

        shift = get_staff_current_shift(staff_id=staff_id)
        finish_result = finish_shift(shift)

        return Response(finish_result)
