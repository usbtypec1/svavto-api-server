from datetime import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status

from shifts.services.shifts import create_unconfirmed_shifts

__all__ = ('ShiftCreateApi',)


class ShiftCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        performer_id = serializers.IntegerField()
        dates = serializers.ListField(child=serializers.DateField())

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        date = serializers.DateField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        performer_id: int = serialized_data['performer_id']
        dates: list[datetime.date] = serialized_data['dates']

        shifts = create_unconfirmed_shifts(
            performer_id=performer_id,
            dates=dates
        )

        serializer = self.OutputSerializer(shifts, many=True)
        response_data = {
            'shifts': serializer.data,
            'performer_id': performer_id,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
