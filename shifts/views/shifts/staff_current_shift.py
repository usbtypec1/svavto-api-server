from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.models import Shift
from shifts.selectors import get_active_shift

__all__ = ('StaffCurrentShiftRetrieveApi',)


class StaffCurrentShiftRetrieveApi(APIView):
    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = Shift
            fields = ('id', 'date')

    def get(self, request: Request, staff_id: int) -> Response:
        active_shift = get_active_shift(staff_id)
        serializer = self.OutputSerializer(active_shift)
        return Response(serializer.data)
