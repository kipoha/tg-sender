import asyncio

from asgiref.sync import async_to_sync

from celery import shared_task

from telethon import TelegramClient

from django.db import IntegrityError

from telegram_sender.models import Campaign, MessageLog
from telegram_sender.utils import create_client

async def connect_send(client: TelegramClient, content_type, contact_value, message_content=None, media_file=None):
    if not client.is_connected():
        await client.connect()

    try:
        if content_type == 'text':
            await client.send_message(contact_value, message_content)
        elif content_type in ['photo', 'video', 'voice', 'round']:
            await client.send_file(contact_value, media_file, caption=message_content)
    except Exception as e:
        raise e


@shared_task()
def send_campaign_messages(campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    accounts = campaign.accounts.all()
    contacts = campaign.contacts.all()
    interval = campaign.send_interval * 60
    max_contacts_per_account = campaign.max_contacts_per_account
    messages_log = []

    for account in accounts:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        client = create_client(account.phone_number)

        for i, contact in enumerate(contacts):
            try:
                content_type = campaign.message.message_type
                message_content = campaign.message.content
                contact_value = contact.contact_value
                media_file = campaign.message.media_file

                loop.run_until_complete(connect_send(client, content_type, contact_value, message_content, media_file))

                messages_log.append(MessageLog(campaign=campaign, account=account, recipient=contact_value, status='sent'))

                if (i + 1) % max_contacts_per_account == 0:
                    loop.run_until_complete(asyncio.sleep(interval))
                else:
                    loop.run_until_complete(asyncio.sleep(interval / 2))

            except Exception as e:
                contact_value = contact.contact_value
                error_message = str(e)
                messages_log.append(MessageLog(campaign=campaign, account=account, recipient=contact_value, status='failed', error_message=error_message))
                print(f"Error sending message to {contact_value}: {error_message}")
        
        if client.is_connected():
            client.disconnect()

    try:
        MessageLog.objects.bulk_create(messages_log)
    except IntegrityError as e:
        print(f"Error saving message logs: {e}")

@async_to_sync
async def test_async():
    print("test_async")
    await asyncio.sleep(5)
    print("test_async end")

@shared_task
def test():
    test_async()

