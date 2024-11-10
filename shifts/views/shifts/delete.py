from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.services.shifts import delete_shift_by_id

__all__ = ('ShiftDeleteApi',)


class ShiftDeleteApi(APIView):

    def delete(self, request: Request, shift_id: int) -> Response:
        delete_shift_by_id(shift_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
