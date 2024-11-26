from uuid import UUID

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.models import CarWashServicePrice
from car_washes.selectors import ensure_car_wash_exists, ensure_service_exists
from car_washes.serializers import (
    CarWashServicePriceUpsertInputSerializer,
    CarWashServicePriceUpsertOutputSerializer,
)

__all__ = ('SpecificCarWashServiceUpdateDeleteApi',)


class SpecificCarWashServiceUpdateDeleteApi(APIView):
    def put(
        self,
        request: Request,
        car_wash_id: int,
        service_id: UUID,
    ) -> Response:
        serializer = CarWashServicePriceUpsertInputSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data
        price: int = serialized_data['price']

        ensure_service_exists(service_id)
        ensure_car_wash_exists(car_wash_id)

        service_price, is_created = (
            CarWashServicePrice.objects.update_or_create(
                car_wash_id=car_wash_id,
                service_id=service_id,
                defaults={
                    'price': price,
                },
            )
        )

        if is_created:
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_200_OK

        serializer = CarWashServicePriceUpsertOutputSerializer(service_price)
        return Response(serializer.data, status_code)

    def delete(
        self,
        request: Request,
        car_wash_id: int,
        service_id: UUID,
    ) -> Response:
        ensure_service_exists(service_id)
        ensure_car_wash_exists(car_wash_id)

        CarWashServicePrice.objects.filter(
            car_wash_id=car_wash_id,
            service_id=service_id,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
