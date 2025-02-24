import asyncio

from asgiref.sync import sync_to_async

from celery import shared_task

from telethon import TelegramClient

from telegram_message_parser.models import MessageError, TelegramChannelGroup

from telegram_sender.utils import create_client

@sync_to_async(thread_sensitive=True)
def create_error_message(channel_id, error, error_detail):
    return MessageError.objects.create(channel=TelegramChannelGroup.objects.get(chat_id=channel_id), error=error, error_detail=error_detail)


async def parse_messages(client: TelegramClient, channel_ids, limit, keywords, send_channel_ids):
    for channel_id in channel_ids: 
        async for message in client.iter_messages(channel_id, limit=limit):
            if message.text and any(keyword.lower() in message.text.lower() for keyword in keywords):
                try:
                    for send_channel_id in send_channel_ids:
                        # await client.forward_messages(send_channel_id, message)
                        await message.forward_to(send_channel_id)
                except Exception as e:
                    import traceback
                    await create_error_message(channel_id, str(e), traceback.format_exc())


@shared_task
def parse_message(channel_ids, send_channel_ids, phonenumber, keywords):
    try:
        channel_ids = channel_ids.splitlines()
        send_channel_ids = send_channel_ids.splitlines()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        client = create_client(phonenumber)
        client.iter_messages
        client.get_messages

        async def fetch_and_parse():
            await client.connect()
            await parse_messages(client, channel_ids, 10, keywords, send_channel_ids)
            client.disconnect()
        try:
            asyncio.run(fetch_and_parse())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(fetch_and_parse())
        except Exception as e:
            import traceback
            MessageError.objects.create(error=str(e), error_detail=traceback.format_exc())
    except Exception as e:
        import traceback
        MessageError.objects.create(error=str(e), error_detail=traceback.format_exc())
