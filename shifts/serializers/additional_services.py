from rest_framework import serializers

__all__ = ('AdditionalServiceSerializer',)


class AdditionalServiceSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    count = serializers.IntegerField(default=1)
