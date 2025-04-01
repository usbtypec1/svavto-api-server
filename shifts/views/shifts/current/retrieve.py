from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.models import WindshieldWasherHidden
from shifts.selectors import get_staff_current_shift
from shifts.serializers import StaffCurrentShiftRetrieveOutputSerializer


__all__ = ("StaffCurrentShiftRetrieveApi",)


class StaffCurrentShiftRetrieveApi(APIView):

    def get(self, request: Request, staff_id: int) -> Response:
        active_shift = get_staff_current_shift(staff_id)
        serializer = StaffCurrentShiftRetrieveOutputSerializer(active_shift)
        is_windshield_washer_hidden = WindshieldWasherHidden.get()
        return Response(
            serializer.data
            | {'is_windshield_washer_hidden': is_windshield_washer_hidden}
        )
