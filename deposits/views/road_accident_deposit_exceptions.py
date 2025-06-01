from django.http.response import Http404
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

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
        response = super().list(request, *args, **kwargs)
        response.data = {'road_accident_deposit_exceptions': response.data}
        return response

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise RoadAccidentDepositExceptionNotFoundError
