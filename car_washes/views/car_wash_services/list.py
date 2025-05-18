from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.serializers.car_wash_services.list import (
    CarWashServiceListInputSerializer,
    CarWashServiceSerializer,
)
from car_washes.use_cases import CarWashServiceListUseCase


class CarWashAllServicesApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = CarWashServiceListInputSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        car_wash_ids: list[int] | None = serialized_data["car_wash_ids"]

        car_wash_services = CarWashServiceListUseCase(
            car_wash_ids=car_wash_ids,
        ).execute()

        serializer = CarWashServiceSerializer(car_wash_services, many=True)
        return Response({"services": serializer.data})
