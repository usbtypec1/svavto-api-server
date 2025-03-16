import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.serializers import (
    CarWashesRevenueReportOutputSerializer,
    CarWashesRevenueReportInputSerializer,
)
from economics.services.reports import get_car_washes_sales_report

__all__ = ("ServiceCostsApi",)


class ServiceCostsApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = CarWashesRevenueReportInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        from_date: datetime.date = serialized_data["from_date"]
        to_date: datetime.date = serialized_data["to_date"]
        car_wash_ids: list[int] = serialized_data["car_wash_ids"]

        report = get_car_washes_sales_report(
            car_wash_ids=car_wash_ids,
            from_date=from_date,
            to_date=to_date,
        )
        response_data = {"car_washes_revenue": report}
        serializer = CarWashesRevenueReportOutputSerializer(response_data)

        return Response(serializer.data)
