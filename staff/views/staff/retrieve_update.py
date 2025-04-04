from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.selectors import get_staff_by_id
from staff.serializers import StaffRetrieveOutputSerializer
from staff.services import update_last_activity_time, update_staff

__all__ = ("StaffRetrieveUpdateApi",)


class StaffRetrieveUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        is_banned = serializers.BooleanField()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        full_name = serializers.CharField(max_length=100)
        car_sharing_phone_number = serializers.CharField(max_length=16)
        console_phone_number = serializers.CharField(max_length=16)
        created_at = serializers.DateTimeField()
        is_banned = serializers.BooleanField()

    def get(self, request: Request, staff_id: int) -> Response:
        staff = get_staff_by_id(staff_id)
        update_last_activity_time(staff_id=staff_id)
        serializer = StaffRetrieveOutputSerializer(staff)
        return Response(serializer.data)

    def put(self, request: Request, staff_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data
        is_banned: bool = serialized_data["is_banned"]
        update_staff(staff_id=staff_id, is_banned=is_banned)
        return Response(status=status.HTTP_204_NO_CONTENT)
