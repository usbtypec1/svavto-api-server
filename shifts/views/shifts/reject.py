from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.exceptions import ShiftNotFoundError
from shifts.serializers import ShiftRejectInputSerializer
from shifts.services.shifts import mark_shift_as_rejected_now

__all__ = ('ShiftRejectApi',)


class ShiftRejectApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = ShiftRejectInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shift_id: int = serializer.validated_data['shift_id']

        is_rejected = mark_shift_as_rejected_now(shift_id)

        if not is_rejected:
            raise ShiftNotFoundError

        return Response(status=status.HTTP_204_NO_CONTENT)
