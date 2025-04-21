from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from bonuses.serializers import BonusesExcludedStaffInputSerializer
from bonuses.use_cases import (
    BonusesExcludedStaffListUseCase,
    BonusesExcludedStaffUpdateUseCase,
)


class BonusesExcludedStaffApi(APIView):

    def get(self, request: Request) -> Response:
        staff_ids = BonusesExcludedStaffListUseCase().execute()
        return Response({'staff_ids': staff_ids})

    def put(self, request: Request) -> Response:
        serializer = BonusesExcludedStaffInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff_ids: list[int] = serializer.validated_data['staff_ids']

        BonusesExcludedStaffUpdateUseCase(staff_ids=staff_ids).execute()

        return Response(status=status.HTTP_204_NO_CONTENT)
