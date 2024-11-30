import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.serializers import ServiceCostsInputSerializer
from economics.services.reports.car_washes_revenue import (
    CarWashesRevenueReportGenerator,
)

__all__ = ('ServiceCostsApi',)


class ServiceCostsApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = ServiceCostsInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        from_date: datetime.date = serialized_data['from_date']
        to_date: datetime.date = serialized_data['to_date']
        car_wash_ids: int = serialized_data['car_wash_ids']

        report_generator = CarWashesRevenueReportGenerator(
            car_wash_ids=car_wash_ids,
            from_date=from_date,
            to_date=to_date,
        )
        response_data = report_generator.generate_report()
        return Response(response_data)
