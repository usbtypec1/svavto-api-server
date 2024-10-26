import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status

from shifts.services.shifts import confirm_shifts

from shifts.tasks import send_staff_shift_confirmation

__all__ = ('ShiftConfirmApi', 'StaffShiftConfirmationSendApi')


class ShiftConfirmApi(APIView):
    class InputSerializer(serializers.Serializer):
        shift_id = serializers.IntegerField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        shift_id: int = serialized_data['shift_id']
        confirm_shifts([shift_id])

        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffShiftConfirmationSendApi(APIView):
    class InputSerializer(serializers.Serializer):
        date = serializers.DateField(default=None)
        staff_shift_ids = serializers.IntegerField(many=True, default=None)

        def validate(self, data):
            if not any((data['date'], data['staff_shift_ids'])):
                raise serializers.ValidationError(
                    'Either "date" or "staff_shift_ids" must be provided.'
                )
            if all((data['date'], data['staff_shift_ids'])):
                raise serializers.ValidationError(
                    'Only either "date" or "staff_shift_ids" must be provided.'
                )
            return data

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        staff_shift_ids: int | None = serialized_data['staff_shift_ids']
        date: datetime.date | None = serializer.validated_data['date']

        send_staff_shift_confirmation.delay(
            staff_shift_ids=staff_shift_ids,
            date=date,
        )

        return Response(status=status.HTTP_202_ACCEPTED)
