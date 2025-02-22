import datetime

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import (
    ShiftExtraCreateInputSerializer, ShiftExtraCreateOutputSerializer,
)
from shifts.services.shifts import ShiftExtraCreateInteractor


class ShiftExtraCreateApi(APIView):

    def post(self, request: Request) -> Response:
        serializer = ShiftExtraCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data: dict = serializer.validated_data

        shifts: list = validated_data['shifts']

        created_shifts = ShiftExtraCreateInteractor(shifts=shifts).execute()

        serializer = ShiftExtraCreateOutputSerializer(
            created_shifts,
            many=True,
        )
        response_data = {'shifts': serializer.data}
        return Response(response_data, status.HTTP_201_CREATED)
