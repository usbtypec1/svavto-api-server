from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status

from shifts.services.shifts import confirm_shifts

__all__ = ('ShiftConfirmApi',)


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
