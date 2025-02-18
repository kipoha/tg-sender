from rest_framework import serializers

class MessageImagesSerializer(serializers.Serializer):
    image = serializers.FileField(required=True)

class MessageCreateSerializer(serializers.Serializer):
    chat_id = serializers.CharField(required=True)
    sender = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    images = MessageImagesSerializer(required=False, many=True)

