import datetime

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

__all__ = ('ReportApi',)

from shifts.services.reports import (
    get_detailed_period_report,
    get_financial_statistics,
)


class ReportInputSerializer(serializers.Serializer):
    from_date = serializers.DateField()
    to_date = serializers.DateField()


class ReportApi(APIView):
    def get(self, request: Request, staff_id: int) -> Response:
        serializer = ReportInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        from_date: datetime.date = serialized_data['from_date']
        to_date: datetime.date = serialized_data['to_date']

        # Get detailed report
        report = get_detailed_period_report(staff_id, from_date, to_date)

        # Get statistics for penalties and surcharges
        financial_stats = get_financial_statistics(staff_id, from_date, to_date)

        return Response({
            'daily_stats': report['daily_stats'],
            'period_totals': report['period_totals'],
            'financial_stats': financial_stats
        })
