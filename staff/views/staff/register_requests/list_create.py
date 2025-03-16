from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.selectors import get_staff_register_requests
from staff.serializers import (
    StaffRegisterRequestCreateInputSerializer,
    StaffRegisterRequestListCreateOutputSerializer,
)
from staff.services import StaffRegisterRequestCreateInteractor

__all__ = ("StaffRegisterRequestListCreateApi",)


class StaffRegisterRequestListCreateApi(APIView):
    def get(self, request: Request) -> Response:
        staff_register_requests = get_staff_register_requests()
        serializer = StaffRegisterRequestListCreateOutputSerializer(
            staff_register_requests,
            many=True,
        )
        return Response({"staff_register_requests": serializer.data})

    def post(self, request: Request) -> Response:
        serializer = StaffRegisterRequestCreateInputSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        interactor = StaffRegisterRequestCreateInteractor(
            staff_id=data["staff_id"],
            full_name=data["full_name"],
            car_sharing_phone_number=data["car_sharing_phone_number"],
            console_phone_number=data["console_phone_number"],
        )
        staff_register_request = interactor.execute()

        serializer = StaffRegisterRequestListCreateOutputSerializer(
            staff_register_request,
        )
        return Response(serializer.data, status.HTTP_201_CREATED)
