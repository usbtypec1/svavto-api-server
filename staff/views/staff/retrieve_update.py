from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.models import StaffType
from staff.selectors import get_staff_by_id
from staff.serializers import StaffRetrieveOutputSerializer
from staff.services import update_last_activity_time, update_staff

__all__ = ("StaffRetrieveUpdateApi",)

from staff.use_cases.staff_update import StaffUpdateUseCase


class StaffRetrieveUpdateApi(APIView):
    class InputSerializer(serializers.Serializer):
        is_banned = serializers.BooleanField()
        type = serializers.ChoiceField(choices=StaffType.choices)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        full_name = serializers.CharField(max_length=100)
        car_sharing_phone_number = serializers.CharField(max_length=16)
        console_phone_number = serializers.CharField(max_length=16)
        created_at = serializers.DateTimeField()
        type = serializers.ChoiceField(choices=StaffType.choices)
        is_banned = serializers.BooleanField()

    def get(self, request: Request, staff_id: int) -> Response:
        staff = get_staff_by_id(staff_id)
        update_last_activity_time(staff_id=staff_id)
        serializer = StaffRetrieveOutputSerializer(staff)
        return Response(serializer.data)

    def put(self, request: Request, staff_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data
        is_banned: bool = data["is_banned"]
        staff_type: int = data["type"]

        StaffUpdateUseCase(
            staff_type=staff_type,
            staff_id=staff_id,
            is_banned=is_banned,
        ).execute()

        return Response(status=status.HTTP_204_NO_CONTENT)
