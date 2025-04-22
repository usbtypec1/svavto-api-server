import datetime

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import BatchEditShiftListInputSerializer
from shifts.serializers.batch_edit import (
    BatchEditShiftListOutputSerializer,
    BatchEditShiftUpdateInputSerializer,
)
from shifts.use_cases.batch_edit_item_list import BatchEditItemListUseCase
from shifts.use_cases.batch_edit_item_update import BatchEditItemUpdateUseCase


class BatchEditApi(APIView):

    def get(self, request: Request) -> Response:
        serializer = BatchEditShiftListInputSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data
        date: datetime.date = data['date']
        staff_id: int = data['staff_id']

        shifts = BatchEditItemListUseCase(
            date=date,
            staff_id=staff_id,
        ).execute()

        serializer = BatchEditShiftListOutputSerializer(shifts, many=True)
        return Response({'shifts': serializer.data})

    def post(self, request: Request) -> Response:
        serializer = BatchEditShiftUpdateInputSerializer(
            data=request.data,
            many=True,
        )
        serializer.is_valid(raise_exception=True)
        items: list[dict] = serializer.validated_data

        BatchEditItemUpdateUseCase(items=items).execute()

        return Response()
