from django.http.response import Http404
from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from deposits.exceptions import FineDepositExceptionNotFoundError
from deposits.models import FineDepositException


class FineDepositExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FineDepositException
        fields = '__all__'


class FineDepositExceptionViewSet(ModelViewSet):
    queryset = FineDepositException.objects.all()
    serializer_class = FineDepositExceptionSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data = {'fine_deposit_exceptions': response.data}
        return response

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            raise FineDepositExceptionNotFoundError
