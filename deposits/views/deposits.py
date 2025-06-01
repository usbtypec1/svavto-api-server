from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from deposits.serializers import (
    DepositListInputSerializer,
    DepositListOutputSerializer,
)
from deposits.use_cases import DepositListUseCase
from shifts.services.report_periods import ReportPeriod


class DepositListApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = DepositListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        from_report_period = ReportPeriod.from_number(
            year=validated_data['from_report_period_year'],
            month=validated_data['from_report_period_month'],
            number=validated_data['from_report_period_number'],
        )
        to_report_period = ReportPeriod.from_number(
            year=validated_data['to_report_period_year'],
            month=validated_data['to_report_period_month'],
            number=validated_data['to_report_period_number'],
        )

        deposits_response = DepositListUseCase(
            from_report_period=from_report_period,
            to_report_period=to_report_period,
        ).execute()

        serializer = DepositListOutputSerializer(deposits_response)
        return Response(serializer.data)
