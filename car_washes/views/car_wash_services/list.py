from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.selectors import (
    get_all_flatten_car_wash_services,
    get_flatten_specific_car_wash_services, get_root_car_wash_services,
)
from car_washes.serializers import CarWashServicesInputSerializer

__all__ = ('SpecificCarWashServiceListApi', 'CarWashAllServicesApi')


class CarWashAllServicesApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = CarWashServicesInputSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        depth: int = serialized_data['depth']
        flat: bool = serialized_data['flat']

        if flat:
            car_wash_services = get_all_flatten_car_wash_services()
        else:
            car_wash_services = get_root_car_wash_services(
                car_wash_id=None,
                depth=depth,
            )
        return Response({'services': car_wash_services})


class SpecificCarWashServiceListApi(APIView):

    def get(self, request: Request, car_wash_id: int) -> Response:
        serializer = CarWashServicesInputSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        depth: int = serialized_data['depth']
        flat: bool = serialized_data['flat']

        if flat:
            car_wash_services = get_flatten_specific_car_wash_services(
                car_wash_id=car_wash_id,
            )
        else:
            car_wash_services = get_root_car_wash_services(
                car_wash_id=car_wash_id,
                depth=depth,
            )
        return Response({'services': car_wash_services})
