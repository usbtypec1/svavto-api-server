from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.serializers.car_wash_service_prices.list import (
    CarWashServicePriceListOutputSerializer,
)
from car_washes.use_cases import CarWashServicePriceListUseCase


class CarWashServicePriceListApi(APIView):

    def get(self, request: Request, car_wash_id: int) -> Response:
        car_wash_service_price_list = CarWashServicePriceListUseCase(
            car_wash_id=car_wash_id,
        ).execute()
        serializer = CarWashServicePriceListOutputSerializer(
            car_wash_service_price_list
        )
        return Response(serializer.data)
