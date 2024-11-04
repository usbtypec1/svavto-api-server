from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.models import Staff
from staff.selectors import get_all_staff
from staff.services import create_staff

__all__ = ('StaffListCreateApi',)


class StaffCreateInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = (
            'id',
            'full_name',
            'car_sharing_phone_number',
            'console_phone_number',
        )



class StaffListCreateApi(APIView):

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        full_name = serializers.CharField()
        car_sharing_phone_number = serializers.CharField()
        console_phone_number = serializers.CharField()
        is_banned = serializers.BooleanField()
        created_at = serializers.DateTimeField()

    def get(self, request: Request) -> Response:
        staff_list = get_all_staff()
        serializer = self.OutputSerializer(staff_list, many=True)
        response_data = {'staff': serializer.data}
        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = StaffCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        create_staff(
            staff_id=serialized_data['id'],
            full_name=serialized_data['full_name'],
            car_sharing_phone_number=(
                serialized_data['car_sharing_phone_number']
            ),
            console_phone_number=serialized_data['console_phone_number']
        )

        return Response(status=status.HTTP_201_CREATED)
