from rest_framework import status, serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from shifts.models import CarToWash, CarToWashAdditionalService
from shifts.serializers import AdditionalServiceSerializer
from shifts.services.cars_to_wash import update_car_to_wash

__all__ = ('RetrieveUpdateCarsToWashApi',)


class CarToWashAdditionalServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarToWashAdditionalService
        fields = ['name', 'count']


class CarToWashDetailSerializer(serializers.ModelSerializer):
    class_type = serializers.CharField(source='car_class')
    additional_services = CarToWashAdditionalServiceSerializer(
        source='cartowashadditionalservice_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = CarToWash
        fields = [
            'id',
            'number',
            'wash_type',
            'class_type',
            'windshield_washer_refilled_bottle_percentage',
            'created_at',
            'additional_services',
        ]


class RetrieveUpdateCarsToWashApi(APIView):
    class InputSerializer(serializers.Serializer):
        additional_services = AdditionalServiceSerializer(many=True)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = CarToWash
            fields = '__all__'
            depth = 1

    def get(self, request: Request, car_id: int) -> Response:
        car = CarToWash.objects.prefetch_related(
            'cartowashadditionalservice_set'
        ).get(id=car_id)

        serializer = CarToWashDetailSerializer(car)
        return Response(serializer.data)

    def patch(self, request: Request, car_id: int) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serialized_data = serializer.data

        additional_services: list[dict] = serialized_data['additional_services']

        update_car_to_wash(
            car_id=car_id,
            additional_services=additional_services,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
