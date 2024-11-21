from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.selectors import (
    get_all_flatten_car_wash_services,
    get_flatten_specific_car_wash_services,
)

__all__ = ('SpecificCarWashServiceListApi', 'CarWashAllServicesApi')


class CarWashAllServicesApi(APIView):

    def get(self, request: Request) -> Response:
        car_wash_services = get_all_flatten_car_wash_services()
        return Response({'services': car_wash_services})


class SpecificCarWashServiceListApi(APIView):

    def get(self, request: Request, car_wash_id: int) -> Response:
        car_wash_services = get_flatten_specific_car_wash_services(
            car_wash_id=car_wash_id,
        )
        return Response({'services': car_wash_services})
