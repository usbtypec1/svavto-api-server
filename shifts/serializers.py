from rest_framework import serializers

__all__ = ('AdditionalServiceSerializer',)


class AdditionalServiceSerializer(serializers.Serializer):
    name = serializers.CharField()
    count = serializers.IntegerField()
