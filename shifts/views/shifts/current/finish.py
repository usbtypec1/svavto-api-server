from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.selectors import get_staff_current_shift
from shifts.serializers import (
    ShiftFinishInputSerializer,
    ShiftFinishOutputSerializer,
)
from shifts.services.shifts import ShiftFinishInteractor, ShiftSummaryInteractor
from staff.selectors import ensure_staff_exists
from staff.services import update_last_activity_time

__all__ = ('ShiftFinishApi',)


class ShiftFinishApi(APIView):
    def post(self, request: Request) -> Response:
        serializer = ShiftFinishInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data: dict = serializer.data

        staff_id: int = serialized_data['staff_id']
        photo_file_ids: list[str] = serialized_data['photo_file_ids']

        ensure_staff_exists(staff_id)
        shift = get_staff_current_shift(staff_id=staff_id)

        shift_summary_interactor = ShiftSummaryInteractor(shift_id=shift.id)
        shift_summary = shift_summary_interactor.execute()

        shift_finish_interactor = ShiftFinishInteractor(
            shift=shift,
            shift_summary=shift_summary,
            photo_file_ids=photo_file_ids,
        )
        shift_finish_result = shift_finish_interactor.finish_shift()

        update_last_activity_time(staff_id=staff_id)

        serializer = ShiftFinishOutputSerializer(shift_finish_result)
        return Response(serializer.data)
