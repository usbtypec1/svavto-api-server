import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.serializers import (
    CarTransporterSurchargeCreateInputSerializer,
    CarTransporterSurchargeCreateOutputSerializer,
    SurchargeListInputSerializer,
    SurchargeListOutputSerializer,
)
from economics.use_cases import (
    CarTransporterSurchargeListUseCase,
    CarTransporterSurchargeCreateUseCase,
    CarTransporterSurchargeDeleteUseCase,
)


class CarTransporterSurchargeListCreateApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = SurchargeListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        staff_ids: list[int] | None = data["staff_ids"]
        limit: int = data["limit"]
        offset: int = data["offset"]

        surcharges_page = CarTransporterSurchargeListUseCase(
            staff_ids=staff_ids,
            limit=limit,
            offset=offset,
        ).execute()

        serializer = SurchargeListOutputSerializer(surcharges_page)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = CarTransporterSurchargeCreateInputSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.validated_data

        staff_id: int = serialized_data["staff_id"]
        date: datetime.date = serialized_data["date"]
        reason: str = serialized_data["reason"]
        amount: int = serialized_data["amount"]

        surcharge = CarTransporterSurchargeCreateUseCase(
            staff_id=staff_id,
            date=date,
            reason=reason,
            amount=amount,
        ).execute()

        serializer = CarTransporterSurchargeCreateOutputSerializer(surcharge)
        return Response(serializer.data, status.HTTP_201_CREATED)


class CarTransporterSurchargeDeleteApi(APIView):

    def delete(self, request: Request, surcharge_id: int) -> Response:
        CarTransporterSurchargeDeleteUseCase(
            surcharge_id=surcharge_id
        ).execute()
        return Response(status=status.HTTP_204_NO_CONTENT)
