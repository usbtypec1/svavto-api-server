from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.selectors import get_car_washes
from car_washes.serializers import (
    CarWashCreateInputSerializer,
    CarWashCreateOutputSerializer,
    CarWashListInputSerializer, CarWashListOutputSerializer,
)
from car_washes.services import create_car_wash

__all__ = ("CarWashListCreateApi",)


class CarWashListCreateApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = CarWashListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data
        include_hidden: bool = data["include_hidden"]

        car_washes = get_car_washes(include_hidden=include_hidden)

        serializer = CarWashListOutputSerializer(car_washes, many=True)
        return Response({"car_washes": serializer.data})

    def post(self, request: Request) -> Response:
        serializer = CarWashCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        name: str = serialized_data["name"]
        comfort_class_car_washing_price: int = serialized_data[
            "comfort_class_car_washing_price"
        ]
        business_class_car_washing_price: int = serialized_data[
            "business_class_car_washing_price"
        ]
        van_washing_price: int = serialized_data["van_washing_price"]
        windshield_washer_price_per_bottle: int = serialized_data[
            "windshield_washer_price_per_bottle"
        ]

        car_wash = create_car_wash(
            name=name,
            comfort_class_car_washing_price=comfort_class_car_washing_price,
            business_class_car_washing_price=business_class_car_washing_price,
            van_washing_price=van_washing_price,
            windshield_washer_price_per_bottle=windshield_washer_price_per_bottle,
        )
        serializer = CarWashCreateOutputSerializer(car_wash)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
