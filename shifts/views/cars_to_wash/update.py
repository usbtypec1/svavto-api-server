from rest_framework import status, serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.serializers import AdditionalServiceSerializer
from shifts.services.cars_to_wash import update_car_to_wash

__all__ = ('UpdateCarsToWashApi',)


class UpdateCarsToWashApi(APIView):
    class InputSerializer(serializers.Serializer):
        additional_services = AdditionalServiceSerializer(many=True)

    def put(self, request: Request, car_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        additional_services: list[dict] = serialized_data['additional_services']

        update_car_to_wash(
            car_id=car_id,
            additional_services=additional_services,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
