from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.selectors import get_all_flatten_car_wash_services
from car_washes.serializers import (
    CarWashServiceListInputSerializer,
    CarWashServiceSerializer,
)

__all__ = ('CarWashAllServicesApi',)


class CarWashAllServicesApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = CarWashServiceListInputSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        car_wash_ids: list[int] | None = serialized_data['car_wash_ids']

        car_wash_services = get_all_flatten_car_wash_services(car_wash_ids)

        serializer = CarWashServiceSerializer(car_wash_services, many=True)
        return Response({'services': serializer.data})
