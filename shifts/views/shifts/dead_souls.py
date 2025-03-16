from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import (
    DeadSoulsInputSerializer,
    DeadSoulsOutputSerializer,
)
from shifts.services import DeadSoulsReadInteractor


__all__ = ("DeadSoulsApi",)


class DeadSoulsApi(APIView):
    def get(self, request: Request):
        serializer = DeadSoulsInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data: dict = serializer.validated_data
        month: int = data["month"]
        year: int = data["year"]

        dead_souls = DeadSoulsReadInteractor(
            month=month,
            year=year,
        ).execute()

        serializer = DeadSoulsOutputSerializer(dead_souls)
        return Response(serializer.data)
