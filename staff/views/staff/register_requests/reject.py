from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.serializers import StaffRegisterRequestRejectInputSerializer
from staff.services import StaffRegisterRequestRejectInteractor

__all__ = ('StaffRegisterRequestRejectApi',)


class StaffRegisterRequestRejectApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = StaffRegisterRequestRejectInputSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        request_id: int = data['staff_register_request_id']
        interactor = StaffRegisterRequestRejectInteractor(request_id=request_id)
        interactor.execute()

        return Response(status=status.HTTP_204_NO_CONTENT)
