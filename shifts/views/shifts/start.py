from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.services import ShiftStartInteractor
from staff.services import update_last_activity_time


__all__ = ('ShiftStartApi',)


class ShiftStartInputSerializer(serializers.Serializer):
    shift_id = serializers.IntegerField()


class ShiftStartApi(APIView):
    """API endpoint is used by staff to start their shift."""

    def post(self, request: Request) -> Response:
        serializer = ShiftStartInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shift_id: int = serializer.validated_data['shift_id']

        start_result = ShiftStartInteractor(shift_id=shift_id).execute()
        update_last_activity_time(staff_id=start_result.staff_id)

        return Response()
