from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.serializers.car_washes.retrieve import (
    CarWashRetrieveOutputSerializer
)
from car_washes.serializers.car_washes.update import (
    CarWashUpdateInputSerializer,
    CarWashUpdateOutputSerializer,
)
from car_washes.services import delete_car_wash
from car_washes.use_cases.car_wash_retrieve import CarWashRetrieveUseCase
from car_washes.use_cases.car_wash_update import (
    CarWashUpdateRequestData,
    CarWashUpdateUseCase,
)


class CarWashRetrieveUpdateDeleteApi(APIView):
    def get(self, request: Request, car_wash_id: int) -> Response:
        car_wash = CarWashRetrieveUseCase(car_wash_id=car_wash_id).execute()

        serializer = CarWashRetrieveOutputSerializer(car_wash)
        response_data = serializer.data
        return Response(response_data)

    def put(self, request: Request, car_wash_id: int) -> Response:
        serializer = CarWashUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data: CarWashUpdateRequestData = serializer.data

        car_wash = CarWashUpdateUseCase(
            car_wash_id=car_wash_id,
            data=data,
        ).execute()

        serializer = CarWashUpdateOutputSerializer(car_wash)
        return Response(serializer.data)

    def delete(self, request: Request, car_wash_id: int) -> Response:
        delete_car_wash(car_wash_id=car_wash_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
