from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from performers.selectors import get_performer_by_telegram_id
from performers.services import update_performer

__all__ = ('PerformerRetrieveUpdateApi',)


class PerformerRetrieveUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        is_banned = serializers.BooleanField()

    class OutputSerializer(serializers.Serializer):
        telegram_id = serializers.IntegerField()
        full_name = serializers.CharField(max_length=100)
        car_sharing_phone_number = serializers.CharField(max_length=16)
        console_phone_number = serializers.CharField(max_length=16)

    def get(self, request: Request, telegram_id: int) -> Response:
        performer = get_performer_by_telegram_id(telegram_id)
        serializer = self.OutputSerializer(performer)
        return Response(serializer.data)

    def put(self, request: Request, telegram_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data
        is_banned: bool = serialized_data['is_banned']
        update_performer(telegram_id=telegram_id, is_banned=is_banned)
        return Response(status=status.HTTP_204_NO_CONTENT)
