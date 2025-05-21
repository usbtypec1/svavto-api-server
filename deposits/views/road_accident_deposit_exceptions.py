from django.http.response import Http404
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.response import Response

from deposits.exceptions import RoadAccidentDepositExceptionNotFoundError
from deposits.models import RoadAccidentDepositException


class RoadAccidentDepositExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadAccidentDepositException
        fields = '__all__'


class RoadAccidentDepositExceptionViewSet(ModelViewSet):
    queryset = RoadAccidentDepositException.objects.all()
    serializer_class = RoadAccidentDepositExceptionSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'road_accident_deposit_exceptions': serializer.data})

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise RoadAccidentDepositExceptionNotFoundError
