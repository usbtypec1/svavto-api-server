from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.serializers import (
    StaffShiftsStatisticsReportInputSerializer,
    StaffShiftsStatisticsReportOutputSerializer,
)
from economics.use_cases import StaffShiftsStatisticsUseCase


__all__ = ("StaffShiftsStatisticsReportApi",)


class StaffShiftsStatisticsReportApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = StaffShiftsStatisticsReportInputSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.validated_data

        year: int = serialized_data["year"]
        month: int = serialized_data["month"]
        staff_ids: list[int] | None = serialized_data["staff_ids"]
        report_period_number: int = serialized_data["report_period_number"]

        staff_shifts_statistics = StaffShiftsStatisticsUseCase(
            year=year,
            month=month,
            staff_ids=staff_ids,
            report_period_number=report_period_number,
        ).execute()

        serializer = StaffShiftsStatisticsReportOutputSerializer(
            staff_shifts_statistics,
        )
        return Response(serializer.data)
