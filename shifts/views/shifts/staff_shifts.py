from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.models import Shift


class StaffShiftsListApi(APIView):

    def get(self, request: Request, staff_id: int) -> Response:
        Shift.objects.values('date', 'is_confirmed', 'car_wash')
        return Response()