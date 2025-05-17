from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from car_washes.selectors import (
    get_car_wash_by_id,
    get_flatten_specific_car_wash_services,
)
from car_washes.serializers import (
    CarWashRetrieveOutputSerializer,
    CarWashUpdateInputSerializer,
    CarWashUpdateOutputSerializer,
)
from car_washes.services import delete_car_wash, update_car_wash


class CarWashRetrieveUpdateDeleteApi(APIView):
    def get(self, request: Request, car_wash_id: int) -> Response:
        car_wash = get_car_wash_by_id(car_wash_id)
        car_wash_services = get_flatten_specific_car_wash_services(car_wash_id)
        serializer = CarWashRetrieveOutputSerializer(car_wash)
        response_data = serializer.data
        response_data["services"] = car_wash_services
        return Response(response_data, status=status.HTTP_200_OK)

    def put(self, request: Request, car_wash_id: int) -> Response:
        serializer = CarWashUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        name: str = serialized_data["name"]
        comfort_class_car_washing_price: int = serialized_data[
            "comfort_class_car_washing_price"
        ]
        business_class_car_washing_price: int = serialized_data[
            "business_class_car_washing_price"
        ]
        van_washing_price: int = serialized_data["van_washing_price"]
        windshield_washer_price_per_bottle: int = serialized_data[
            "windshield_washer_price_per_bottle"
        ]
        is_hidden: bool = serialized_data["is_hidden"]

        car_wash = get_car_wash_by_id(car_wash_id)

        car_wash = update_car_wash(
            car_wash=car_wash,
            name=name,
            comfort_class_car_washing_price=comfort_class_car_washing_price,
            business_class_car_washing_price=business_class_car_washing_price,
            van_washing_price=van_washing_price,
            windshield_washer_price_per_bottle=windshield_washer_price_per_bottle,
            is_hidden=is_hidden,
        )
        serializer = CarWashUpdateOutputSerializer(car_wash)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, car_wash_id: int) -> Response:
        delete_car_wash(car_wash_id=car_wash_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
