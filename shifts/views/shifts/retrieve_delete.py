from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.selectors import get_shift_by_id
from shifts.serializers import ShiftRetrieveOutputSerializer
from shifts.services import ShiftDeleteByIdInteractor


__all__ = ('ShiftRetrieveDeleteApi',)


class ShiftRetrieveDeleteApi(APIView):

    def get(self, request: Request, shift_id: int) -> Response:
        shift = get_shift_by_id(shift_id)
        serializer = ShiftRetrieveOutputSerializer(shift)
        return Response(serializer.data)

    def delete(self, request: Request, shift_id: int) -> Response:
        ShiftDeleteByIdInteractor(shift_id).execute()
        return Response(status=status.HTTP_204_NO_CONTENT)
