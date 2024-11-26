import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.exceptions import StaffHasNoAnyShiftError
from shifts.models import Shift

__all__ = ('ShiftLastCreatedDateListApi',)

from staff.selectors import ensure_staff_exists


class ShiftLastCreatedDateListApi(APIView):
    def get(self, request: Request, staff_id: int) -> Response:
        ensure_staff_exists(staff_id)
        shift = (
            Shift.objects.filter(staff_id=staff_id)
            .order_by('-created_at')
            .values('date')
            .first()
        )
        if shift is None:
            raise StaffHasNoAnyShiftError
        date: datetime.date = shift['date']
        shift_dates = Shift.objects.filter(
            staff_id=staff_id,
            date__month=date.month,
            date__year=date.year,
        ).values_list('date', flat=True)
        return Response({'shift_dates': shift_dates})
