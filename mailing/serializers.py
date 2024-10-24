from rest_framework import serializers

__all__ = ('ButtonSerializer', 'MailingSerializer')


class ButtonSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=64)
    url = serializers.URLField()


class MailingSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=4096)
    reply_markup = serializers.ListField(
        child=ButtonSerializer(many=True, required=False),
        default=None,
    )
