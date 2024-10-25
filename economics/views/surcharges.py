from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status

from economics.services import create_surcharge_and_send_notification

__all__ = ('SurchargeCreateApi',)


class SurchargeCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        staff_id = serializers.IntegerField()
        reason = serializers.CharField(max_length=255)
        amount = serializers.IntegerField(min_value=0)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        staff_id = serializers.IntegerField()
        reason = serializers.CharField()
        amount = serializers.IntegerField()
        created_at = serializers.DateTimeField()
        is_notification_delivered = serializers.BooleanField()

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        staff_id: int = serialized_data['staff_id']
        reason: str = serialized_data['reason']
        amount: int = serialized_data['amount']

        surcharge_create_result = create_surcharge_and_send_notification(
            staff_id=staff_id,
            reason=reason,
            amount=amount,
        )

        serializer = self.OutputSerializer(surcharge_create_result)
        return Response(serializer.data, status.HTTP_201_CREATED)
