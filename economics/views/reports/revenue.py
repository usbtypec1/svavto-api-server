import datetime

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

__all__ = ('RevenueReportApi',)


class RevenueReportInputSerializer(serializers.Serializer):
    car_wash_id = serializers.IntegerField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()


class RevenueReportApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = RevenueReportInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.validated_data

        car_wash_id: int = serialized_data['car_wash_id']
        from_date: datetime.date = serialized_data['from_date']
        to_date: datetime.date = serialized_data['to_date']



        return Response()
