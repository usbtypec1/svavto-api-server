from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.selectors import get_all_flatten_car_wash_services

__all__ = ('CarWashAllServicesApi',)


class CarWashAllServicesApi(APIView):

    def get(self, request: Request) -> Response:
        car_wash_services = get_all_flatten_car_wash_services()
        return Response({'services': car_wash_services})
