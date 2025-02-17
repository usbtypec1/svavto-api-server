from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import (
    StaffWithoutShiftsInputSerializer,
    StaffWithoutShiftsOutputSerializer,
)
from shifts.services.shifts import StaffWithoutShiftsForMonthReadInteractor

__all__ = ('StaffWithoutShiftsApi',)


class StaffWithoutShiftsApi(APIView):

    def get(self, request: Request):
        serializer = StaffWithoutShiftsInputSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data

        month: int = data['month']
        year: int = data['year']

        interactor = StaffWithoutShiftsForMonthReadInteractor(
            month=month,
            year=year,
        )
        staff_without_shifts = interactor.execute()

        serializer = StaffWithoutShiftsOutputSerializer(staff_without_shifts)
        return Response(serializer.data)
