from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.selectors import get_all_staff
from staff.services import create_staff

__all__ = ('StaffListCreateApi',)


class StaffListCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        telegram_id = serializers.IntegerField()
        full_name = serializers.CharField(max_length=100)
        car_sharing_phone_number = serializers.CharField(max_length=16)
        console_phone_number = serializers.CharField(max_length=16)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        telegram_id = serializers.IntegerField()
        full_name = serializers.CharField()
        car_sharing_phone_number = serializers.CharField()
        console_phone_number = serializers.CharField()
        is_banned = serializers.BooleanField()
        created_at = serializers.DateTimeField()

    def get(self, request: Request) -> Response:
        performers = get_all_staff()
        serializer = self.OutputSerializer(performers, many=True)
        response_data = {'staff': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        create_staff(
            telegram_id=serialized_data['telegram_id'],
            full_name=serialized_data['full_name'],
            car_sharing_phone_number=(
                serialized_data['car_sharing_phone_number']
            ),
            console_phone_number=serialized_data['console_phone_number']
        )

        return Response(status=status.HTTP_201_CREATED)
