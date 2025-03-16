from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.selectors import get_surcharges_page
from economics.serializers import (
    SurchargeCreateInputSerializer,
    SurchargeCreateOutputSerializer,
    SurchargeListInputSerializer,
    SurchargeListOutputSerializer,
)
from economics.services.penalties import (
    CarTransporterSurchargeDeleteInteractor,
)
from economics.services.surcharges import create_surcharge
from shifts.services.shifts.validators import ensure_shift_exists


__all__ = ("SurchargeCreateApi", "CarTransporterSurchargeDeleteApi")


class SurchargeCreateApi(APIView):
    def get(self, request: Request) -> Response:
        serializer = SurchargeListInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        staff_ids: list[int] | None = data["staff_ids"]
        limit: int = data["limit"]
        offset: int = data["offset"]

        surcharges_page = get_surcharges_page(
            staff_ids=staff_ids,
            limit=limit,
            offset=offset,
        )

        serializer = SurchargeListOutputSerializer(surcharges_page)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = SurchargeCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.validated_data

        shift_id: int = serialized_data["shift_id"]
        reason: str = serialized_data["reason"]
        amount: int = serialized_data["amount"]

        ensure_shift_exists(shift_id)
        surcharge = create_surcharge(
            shift_id=shift_id,
            reason=reason,
            amount=amount,
        )

        serializer = SurchargeCreateOutputSerializer(surcharge)
        return Response(serializer.data, status.HTTP_201_CREATED)


class CarTransporterSurchargeDeleteApi(APIView):
    def delete(self, request: Request, surcharge_id: int) -> Response:
        interactor = CarTransporterSurchargeDeleteInteractor(
            surcharge_id=surcharge_id,
        )
        interactor.execute()
        return Response(status=status.HTTP_204_NO_CONTENT)
