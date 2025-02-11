import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.serializers import (
    CarWashSurchargeCreateInputSerializer,
    CarWashSurchargeListCreateOutputSerializer,
    CarWashSurchargeListInputSerializer,
)
from economics.services.car_washes.surcharges import (
    CarWashSurchargeCreateInteractor,
    CarWashSurchargeListInteractor,

)

__all__ = ('CarWashSurchargeListCreateApi',)


class CarWashSurchargeListCreateApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = CarWashSurchargeListInputSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        from_date: datetime.date | None = data['from_date']
        to_date: datetime.date | None = data['to_date']
        car_wash_ids: list[int] | None = data['car_wash_ids']

        interactor = CarWashSurchargeListInteractor(
            from_date=from_date,
            to_date=to_date,
            car_wash_ids=car_wash_ids,
        )
        surcharges = interactor.execute()

        serializer = CarWashSurchargeListCreateOutputSerializer(
            surcharges,
            many=True,
        )
        return Response({'surcharges': serializer.data})

    def post(self, request: Request) -> Response:
        serializer = CarWashSurchargeCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        car_wash_id: int = data['car_wash_id']
        reason: str = data['reason']
        amount: int = data['amount']

        interactor = CarWashSurchargeCreateInteractor(
            car_wash_id=car_wash_id,
            reason=reason,
            amount=amount,
        )
        surcharge = interactor.execute()

        serializer = CarWashSurchargeListCreateOutputSerializer(surcharge)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
