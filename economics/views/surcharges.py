from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from economics.serializers import (
    SurchargeCreateInputSerializer,
    SurchargeCreateOutputSerializer,
)
from economics.services.surcharges import create_surcharge
from shifts.services.shifts import ensure_shift_exists
from staff.selectors import ensure_staff_exists

__all__ = ('SurchargeCreateApi',)


class SurchargeCreateApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = SurchargeCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.validated_data

        shift_id: int = serialized_data['shift_id']
        staff_id: int = serialized_data['staff_id']
        reason: str = serialized_data['reason']
        amount: int = serialized_data['amount']

        ensure_shift_exists(shift_id)
        ensure_staff_exists(staff_id)
        surcharge = create_surcharge(
            shift_id=shift_id,
            staff_id=staff_id,
            reason=reason,
            amount=amount,
        )

        serializer = SurchargeCreateOutputSerializer(surcharge)
        return Response(serializer.data, status.HTTP_201_CREATED)
