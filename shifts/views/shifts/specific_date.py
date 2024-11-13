import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.models import Shift
from shifts.serializers import (
    DateSerializer,
    ShiftListForSpecificDateOutputSerializer,
)

__all__ = ('ShiftListForSpecificDateApi',)


class ShiftListForSpecificDateApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = DateSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        shifts_date: datetime.date = serialized_data['date']

        shifts = Shift.objects.filter(
            date=shifts_date,
            started_at__isnull=True,
            finished_at__isnull=True,
        )

        serializer = ShiftListForSpecificDateOutputSerializer(shifts, many=True)
        return Response({'shifts': serializer.data})
