from rest_framework import serializers


class BatchEditInputSerializer(serializers.Serializer):
    date = serializers.DateField()
    staff_id = serializers.IntegerField(default=None)


class AdditionalServiceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    count = serializers.IntegerField()


class CarSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    number = serializers.CharField()
    car_wash_id = serializers.IntegerField(allow_null=True)
    car_wash_name = serializers.CharField()
    class_type = serializers.CharField()
    wash_type = serializers.CharField()
    windshield_washer_type = serializers.CharField()
    windshield_washer_refilled_bottle_percentage = serializers.IntegerField()
    additional_services = AdditionalServiceSerializer(many=True)


class BatchEditOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.DateField()
    staff_id = serializers.IntegerField()
    staff_full_name = serializers.CharField()
    cars = CarSerializer(many=True)
