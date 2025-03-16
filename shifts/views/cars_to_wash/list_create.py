from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.selectors import get_staff_current_shift
from shifts.serializers import (
    TransferredCarCreateInputSerializer,
    CarToWashCreateOutputSerializer,
    TransferredCarListInputSerializer,
    TransferredCarListOutputSerializer,
)
from shifts.services import TransferredCarListInteractor
from shifts.services.cars_to_wash import create_car_to_wash
from staff.services import update_last_activity_time


class TransferredCarListCreateApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = TransferredCarListInputSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)
        shift_id: int = serializer.validated_data["shift_id"]

        interactor = TransferredCarListInteractor(shift_id=shift_id)
        transferred_cars = interactor.execute()

        serializer = TransferredCarListOutputSerializer(transferred_cars)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = TransferredCarCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.validated_data

        staff_id: int = serialized_data["staff_id"]
        number: str = serialized_data["number"]
        car_class: str = serialized_data["car_class"]
        wash_type: str = serialized_data["wash_type"]
        windshield_washer_refilled_bottle_percentage: int = serialized_data[
            "windshield_washer_refilled_bottle_percentage"
        ]
        additional_services = serialized_data["additional_services"]

        shift = get_staff_current_shift(staff_id)
        car_wash = create_car_to_wash(
            shift=shift,
            number=number,
            car_class=car_class,
            wash_type=wash_type,
            windshield_washer_refilled_bottle_percentage=(
                windshield_washer_refilled_bottle_percentage
            ),
            additional_services=additional_services,
        )
        update_last_activity_time(staff_id=staff_id)

        serializer = CarToWashCreateOutputSerializer(car_wash)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
