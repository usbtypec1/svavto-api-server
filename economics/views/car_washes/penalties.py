import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.serializers import (
    CarWashPenaltyCreateInputSerializer,
    CarWashPenaltyListCreateOutputSerializer,
    CarWashPenaltyListInputSerializer,
)
from economics.services.car_washes.penalties import (
    CarWashPenaltyCreateInteractor,
    CarWashPenaltyDeleteInteractor,
    CarWashPenaltyListInteractor,
)

__all__ = ("CarWashPenaltyListCreateApi", "CarWashPenaltyDeleteApi")


class CarWashPenaltyDeleteApi(APIView):
    def delete(self, request: Request, penalty_id: int) -> Response:
        interactor = CarWashPenaltyDeleteInteractor(penalty_id=penalty_id)
        interactor.execute()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CarWashPenaltyListCreateApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = CarWashPenaltyListInputSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        from_date: datetime.date | None = data["from_date"]
        to_date: datetime.date | None = data["to_date"]
        car_wash_ids: list[int] | None = data["car_wash_ids"]

        interactor = CarWashPenaltyListInteractor(
            from_date=from_date,
            to_date=to_date,
            car_wash_ids=car_wash_ids,
        )
        penalties = interactor.execute()

        serializer = CarWashPenaltyListCreateOutputSerializer(
            penalties,
            many=True,
        )
        return Response({"penalties": serializer.data})

    def post(self, request: Request) -> Response:
        serializer = CarWashPenaltyCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        car_wash_id: int = data["car_wash_id"]
        reason: str = data["reason"]
        amount: int = data["amount"]
        date: datetime.date = data["date"]

        interactor = CarWashPenaltyCreateInteractor(
            car_wash_id=car_wash_id,
            reason=reason,
            amount=amount,
            date=date,
        )
        penalty = interactor.execute()

        serializer = CarWashPenaltyListCreateOutputSerializer(penalty)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
