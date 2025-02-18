from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from telegram_message_parser.serializers import MessageCreateSerializer
from telegram_message_parser.models import TelegramMessage, TelegramMessageImages, TelegramChannelGroup

# Create your views here.


class CreateMessageView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = MessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            try:
                chat = TelegramChannelGroup.objects.get(chat_id=data["chat_id"])
            except TelegramChannelGroup.DoesNotExist:
                return Response({"error": "Chat not found"}, status=404)
            message = TelegramMessage.objects.create(
                chat=chat,
                sender=data["sender"],
                text=data["text"],
            )

            images = []
            for image_data in request.FILES.getlist("images"):
                images.append(TelegramMessageImages(message=message, image=image_data))

            if images:
                TelegramMessageImages.objects.bulk_create(images)

            return Response({"success": True, "message_id": message.id})

        return Response(serializer.errors, status=400)
        # serializer = MessageCreateSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # print(serializer.data)
        # images = request.FILES.get("images", [])
        # image_serializer = MessageImagesSerializer(data=images, many=True)
        # print(image_serializer.data)
        # return Response({"status": "ok"}, status=200)
