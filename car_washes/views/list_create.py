from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.selectors import get_car_washes
from car_washes.serializers import (
    CarWashCreateInputSerializer,
    CarWashCreateOutputSerializer,
    CarWashListInputSerializer,
    CarWashListOutputSerializer,
)
from car_washes.use_cases.car_wash_create import (
    CarWashCreateRequestData,
    CarWashCreateUseCase,
)


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
        data: CarWashCreateRequestData = serializer.data

        car_wash = CarWashCreateUseCase(data=data).execute()

        serializer = CarWashCreateOutputSerializer(car_wash)
        return Response(serializer.data, status.HTTP_201_CREATED)
