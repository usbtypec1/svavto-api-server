from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.selectors import get_car_wash_by_id
from car_washes.serializers import CarWashSerializer
from car_washes.services import update_car_wash, delete_car_wash


class CarWashRetrieveUpdateDeleteApi(APIView):
    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=100)

    def get(self, request: Request, car_wash_id: int) -> Response:
        car_wash = get_car_wash_by_id(car_wash_id)
        serializer = CarWashSerializer(car_wash)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request, car_wash_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data
        update_car_wash(
            car_wash_id=car_wash_id,
            name=serialized_data['name']
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request: Request, car_wash_id: int) -> Response:
        delete_car_wash(car_wash_id=car_wash_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
