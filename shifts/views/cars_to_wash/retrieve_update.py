from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.exceptions import CarToWashNotFoundError
from shifts.models import CarToWash
from shifts.selectors import get_staff_id_by_car_id
from shifts.serializers import (
    CarToWashDetailOutputSerializer,
    TransferredCarUpdateInputSerializer,
)
from shifts.services.cars_to_wash import CarTransferUpdateInteractor
from staff.services import update_last_activity_time


__all__ = ('RetrieveUpdateCarsToWashApi',)


class RetrieveUpdateCarsToWashApi(APIView):

    def get(self, request: Request, car_id: int) -> Response:
        try:
            car = (
                CarToWash.objects.select_related('car_wash')
                .prefetch_related('additional_services')
                .get(id=car_id)
            )
        except CarToWash.DoesNotExist:
            raise CarToWashNotFoundError(car_to_wash_id=car_id)

        serializer = CarToWashDetailOutputSerializer(car)
        return Response(serializer.data)

    def patch(self, request: Request, car_id: int) -> Response:
        serializer = TransferredCarUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff_id = get_staff_id_by_car_id(car_id)
        interactor = CarTransferUpdateInteractor(
            car_id=car_id,
            **serializer.validated_data
        )
        interactor.execute()

        update_last_activity_time(staff_id=staff_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
