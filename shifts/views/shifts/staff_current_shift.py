from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.exceptions import StaffHasNoActiveShiftError
from shifts.models import Shift

__all__ = ('StaffCurrentShiftRetrieveApi',)


class StaffCurrentShiftRetrieveApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Shift
            fields = ('id', 'date')

    def get(self, request: Request, staff_id: int) -> Response:
        try:
            active_shift = Shift.objects.get(
                staff_id=staff_id,
                is_active=True,
                is_confirmed=True,
            )
            serializer = self.OutputSerializer(active_shift)
            return Response(serializer.data)
        except Shift.DoesNotExist:
            raise StaffHasNoActiveShiftError
