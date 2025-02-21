import asyncio

from asgiref.sync import sync_to_async

from celery import shared_task

from telethon.tl.types import MessageMediaPhoto

from telegram_message_parser.models import TelegramMessageImages, TelegramMessage, MessageError, TelegramChannelGroup

from telegram_sender.utils import create_client

@sync_to_async(thread_sensitive=True)
def create_message(channel_id, sender, text):
    return TelegramMessage.objects.create(chat=TelegramChannelGroup.objects.get(chat_id=channel_id), sender=sender, text=text)

@sync_to_async(thread_sensitive=True)
def create_message_image(message, image):
    return TelegramMessageImages.objects.create(message=message, image=image)

@sync_to_async(thread_sensitive=True)
def create_error_message(channel_id, error, error_detail):
    return MessageError.objects.create(channel=TelegramChannelGroup.objects.get(chat_id=channel_id), error=error, error_detail=error_detail)


async def check_chat_access(client, channel_id):
    try:
        await client.get_entity(channel_id)
        return True, None
    except Exception as e:
        import traceback
        return False, traceback.format_exc()


async def parse_messages(client, channel_id, limit, keywords):
    success, error = await check_chat_access(client, channel_id)
    if not success:
        await create_error_message(channel_id, "Chat not found", error)
        return
    async for message in client.iter_messages(channel_id, limit=limit):
        if message.text and any(keyword.lower() in message.text.lower() for keyword in keywords):
            try:
                msg_obj = await create_message(channel_id, getattr(message.sender, "username", "Unknown"), message.text)
                if message.media and isinstance(message.media, MessageMediaPhoto):
                    image_path = await client.download_media(message)
                    await create_message_image(msg_obj, image_path)
            except Exception as e:
                import traceback
                await create_error_message(channel_id, str(e), traceback.format_exc())


@shared_task
def parse_message(channel_id, phonenumber, keywords):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        client = create_client(phonenumber)
        client.iter_messages
        client.get_messages

        async def fetch_and_parse():
            await client.connect()
            await parse_messages(client, channel_id, 100, keywords)
            client.disconnect()
        try:
            asyncio.run(fetch_and_parse())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(fetch_and_parse())
        except Exception as e:
            import traceback
            print(traceback.format_exc())
    except Exception as e:
        import traceback
        MessageError.objects.create(channel=TelegramChannelGroup.objects.get(chat_id=channel_id), error=str(e), error_detail=traceback.format_exc())
