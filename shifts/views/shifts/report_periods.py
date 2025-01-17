from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import StaffReportPeriodsOutputSerializer
from shifts.services.report_periods import StaffReportPeriodsReadInteractor

__all__ = ('StaffReportPeriodsListApi',)


class StaffReportPeriodsListApi(APIView):
    """
    Get all report periods for a staff member based on all shifts he had.
    """

    def get(self, request: Request, staff_id: int) -> Response:
        interactor = StaffReportPeriodsReadInteractor(staff_id=staff_id)
        staff_report_periods = interactor.execute()

        serializer = StaffReportPeriodsOutputSerializer(staff_report_periods)
        return Response(serializer.data)
