from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.selectors import get_all_staff
from staff.serializers import (
    StaffCreateInputSerializer,
    StaffListInputSerializer,
    StaffListOutputSerializer,
)
from staff.services import create_staff

__all__ = ('StaffListCreateApi', 'StaffListOutputSerializer')


class StaffListCreateApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = StaffListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data
        order_by: str = serialized_data['order_by']

        staff_list = get_all_staff(order_by=order_by)
        serializer = StaffListOutputSerializer(staff_list, many=True)
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
            console_phone_number=serialized_data['console_phone_number'],
        )

        return Response(status=status.HTTP_201_CREATED)
