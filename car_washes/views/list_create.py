from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.selectors import get_car_washes
from car_washes.serializers import (
    CarWashCreateInputSerializer,
    CarWashCreateOutputSerializer,
    CarWashListOutputSerializer,
)
from car_washes.services import create_car_wash

__all__ = ('CarWashListCreateApi',)


class CarWashListCreateApi(APIView):

    def get(self, request: Request) -> Response:
        car_washes = get_car_washes()
        serializer = CarWashListOutputSerializer(car_washes, many=True)
        return Response({'car_washes': serializer.data})

    def post(self, request: Request) -> Response:
        serializer = CarWashCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data
        car_wash = create_car_wash(name=serialized_data['name'])
        serializer = CarWashCreateOutputSerializer(car_wash)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
