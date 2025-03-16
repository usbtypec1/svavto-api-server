from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.services import StaffShiftsMonthListInteractor
from shifts.serializers import StaffShiftsMonthListOutputSerializer


class StaffShiftsMonthListApi(APIView):
    def get(self, request: Request, staff_id: int) -> Response:
        months = StaffShiftsMonthListInteractor(staff_id=staff_id).execute()
        serializer = StaffShiftsMonthListOutputSerializer(months)
        return Response(serializer.data)
