import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.serializers import (
    StaffShiftsStatisticsReportInputSerializer,
    StaffShiftsStatisticsReportOutputSerializer,
)
from economics.services.reports.staff_shifts_statistics import (
    get_staff_shifts_statistics,
)

__all__ = ('StaffShiftsStatisticsReportApi',)


class StaffShiftsStatisticsReportApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = StaffShiftsStatisticsReportInputSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.validated_data

        from_date: datetime.date = serialized_data['from_date']
        to_date: datetime.date = serialized_data['to_date']
        staff_ids: list[int] | None = serialized_data['staff_ids']

        staff_shifts_statistics = get_staff_shifts_statistics(
            from_date=from_date,
            to_date=to_date,
            staff_ids=staff_ids,
        )
        response_data = {'staff_list': staff_shifts_statistics}
        serializer = StaffShiftsStatisticsReportOutputSerializer(
            response_data
        )
        return Response(serializer.data)
