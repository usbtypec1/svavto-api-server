import datetime

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.services.reports import StaffRevenueReportGenerator

__all__ = ('StaffRevenueReportApi',)


class StaffRevenueReportInputSerializer(serializers.Serializer):
    car_wash_id = serializers.IntegerField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()


class StaffRevenueReportApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = StaffRevenueReportInputSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.validated_data

        car_wash_id: int = serialized_data['car_wash_id']
        from_date: datetime.date = serialized_data['from_date']
        to_date: datetime.date = serialized_data['to_date']

        report_generator = StaffRevenueReportGenerator(
            car_wash_id=car_wash_id,
            from_date=from_date,
            to_date=to_date,
        )
        response_data = report_generator.generate_report()
        return Response(response_data)
