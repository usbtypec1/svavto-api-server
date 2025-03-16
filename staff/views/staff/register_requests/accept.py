from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.serializers import (
    StaffItemSerializer,
    StaffRegisterRequestAcceptInputSerializer,
)
from staff.services import StaffRegisterRequestAcceptInteractor

__all__ = ("StaffRegisterRequestAcceptApi",)


class StaffRegisterRequestAcceptApi(APIView):
    def post(self, request: Request) -> Response:
        serializer = StaffRegisterRequestAcceptInputSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        request_id: int = data["staff_register_request_id"]
        interactor = StaffRegisterRequestAcceptInteractor(request_id=request_id)
        staff = interactor.execute()

        serializer = StaffItemSerializer(staff)
        return Response(serializer.data)
