from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from shifts.models import AvailableDate
from shifts.serializers import AvailableDateSerializer

__all__ = ("AvailableDateApi",)


class AvailableDateApi(
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    queryset = AvailableDate.objects.all()
    serializer_class = AvailableDateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"available_dates": serializer.data})

    def get_queryset(self):
        queryset = AvailableDate.objects.all()
        year = self.request.query_params.get("year", None)
        month = self.request.query_params.get("month", None)

        if year is not None:
            queryset = queryset.filter(year=year)
        if month is not None:
            queryset = queryset.filter(month=month)

        return queryset
