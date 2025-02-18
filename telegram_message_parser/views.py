from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from telegram_message_parser.serializers import MessageCreateSerializer
from telegram_message_parser.models import TelegramMessage, TelegramMessageImages, TelegramChannelGroup, KeyWordModel

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

            sender = data["sender"]
            text = data["text"]

            keywords = list(KeyWordModel.objects.values_list("word", flat=True))
            if not any(keyword.lower() in text.lower() for keyword in keywords):
                return Response({"success": True, "message_id": None}, status=200)

            message = TelegramMessage.objects.create(
                chat=chat,
                sender=sender,
                text=text,
            )

            images = []
            for image_data in request.FILES.getlist("images"):
                images.append(TelegramMessageImages(message=message, image=image_data))

            if images:
                TelegramMessageImages.objects.bulk_create(images)

            return Response({"success": True, "message_id": message.id}, status=200)

        return Response(serializer.errors, status=400)
