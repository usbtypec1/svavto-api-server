import datetime

from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.services.cars_to_wash import (
    get_cars_without_windshield_washer_by_date,
    get_staff_cars_count_by_date,
)

__all__ = ("CarsToWashCountByEachStaffApi", "CarsWithoutWindshieldWasherApi")


class DateSerializer(serializers.Serializer):
    date = serializers.DateField()


class CarsToWashCountByEachStaffApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = DateSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        date: datetime.date = serialized_data["date"]

        staff_cars_count_by_date = get_staff_cars_count_by_date(date)
        return Response(staff_cars_count_by_date)


class CarsWithoutWindshieldWasherApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = DateSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        date: datetime.date = serialized_data["date"]

        cars = get_cars_without_windshield_washer_by_date(date)
        return Response({"cars": cars, "date": date})
