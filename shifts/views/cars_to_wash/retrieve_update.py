from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.selectors import get_staff_id_by_car_id
from shifts.serializers import (
    TransferredCarDetailOutputSerializer,
    TransferredCarUpdateInputSerializer,
)
from shifts.services import TransferredCarRetrieveInteractor
from staff.services import update_last_activity_time
from shifts.use_cases.transferred_car_update import TransferredCarUpdateUseCase


__all__ = ("RetrieveUpdateCarsToWashApi",)


class RetrieveUpdateCarsToWashApi(APIView):
    def get(self, request: Request, car_id: int) -> Response:
        transferred_car = TransferredCarRetrieveInteractor(
            transferred_car_id=car_id,
        ).execute()
        serializer = TransferredCarDetailOutputSerializer(transferred_car)
        return Response(serializer.data)

    def patch(self, request: Request, car_id: int) -> Response:
        serializer = TransferredCarUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        staff_id = get_staff_id_by_car_id(car_id)
        interactor = TransferredCarUpdateUseCase(
            car_id=car_id, **serializer.validated_data
        )
        interactor.execute()

        update_last_activity_time(staff_id=staff_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
