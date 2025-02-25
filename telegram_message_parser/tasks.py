import asyncio

from celery import shared_task

from telethon import TelegramClient

from telegram_message_parser.models import MessageError

from telegram_sender.utils import create_client

async def parse_messages(client: TelegramClient, channel_ids, limit, keywords, send_channel_ids, message_errors):
    for channel_id in channel_ids: 
        async for message in client.iter_messages(channel_id, limit=limit):
            if message.text and any(keyword.lower() in message.text.lower() for keyword in keywords):
                try:
                    for send_channel_id in send_channel_ids:
                        await client.forward_messages(send_channel_id, message)
                        # await message.forward_to(send_entity)
                except Exception as e:
                    import traceback
                    message_errors.append(MessageError(channel=str(channel_id), error=str(e), error_detail=traceback.format_exc()))


@shared_task
def parse_message(channel_ids, send_channel_ids, phonenumber, keywords):
    message_errors = []
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
            await parse_messages(client, channel_ids, 10, keywords, send_channel_ids, message_errors)
            client.disconnect()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(fetch_and_parse())
        except Exception as e:
            import traceback
            message_errors.append(MessageError(error=str(e), error_detail=traceback.format_exc()))
    except Exception as e:
        import traceback
        message_errors.append(MessageError(error=str(e), error_detail=traceback.format_exc()))

    if message_errors:
        try:
            MessageError.objects.bulk_create(message_errors)
        except Exception:
            import traceback
            print(traceback.format_exc())
