from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import ShiftConfirmInputSerializer
from shifts.services import ShiftConfirmInteractor
from staff.services import update_last_activity_time


class ShiftConfirmApi(APIView):
    def post(self, request: Request) -> Response:
        serializer = ShiftConfirmInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shift_id: int = serializer.validated_data["shift_id"]

        confirm_result = ShiftConfirmInteractor(shift_id=shift_id).execute()
        update_last_activity_time(staff_id=confirm_result.staff_id)

        return Response(status=status.HTTP_204_NO_CONTENT)
