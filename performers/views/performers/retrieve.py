from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from performers.selectors import get_performer_by_telegram_id

__all__ = ('PerformerRetrieveApi',)


class PerformerRetrieveApi(APIView):
    class OutputSerializer(serializers.Serializer):
        telegram_id = serializers.IntegerField()
        full_name = serializers.CharField(max_length=100)
        car_sharing_phone_number = serializers.CharField(max_length=16)
        console_phone_number = serializers.CharField(max_length=16)

    def get(self, request: Request, telegram_id: int) -> Response:
        performer = get_performer_by_telegram_id(telegram_id)
        serializer = self.OutputSerializer(performer)
        return Response(serializer.data)
