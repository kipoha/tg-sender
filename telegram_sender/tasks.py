import asyncio

import traceback

from asgiref.sync import async_to_sync

from celery import shared_task

from telethon import TelegramClient

from django.db import IntegrityError

from telegram_sender.models import Campaign, MessageLog
from telegram_sender.utils import create_client

async def connect_send(client: TelegramClient, content_type, contact_value, message_content=None, media_file=None):
    await client.connect()

    if content_type == 'text':
        await client.send_message(contact_value, message_content)
    elif content_type in ['photo', 'video', 'voice', 'round']:
        await client.send_file(contact_value, media_file, caption=message_content)


@shared_task()
def send_campaign_messages(campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    campaign.status = 'running'
    campaign.save()
    accounts = campaign.accounts.all()
    contacts = [c for contact in campaign.contacts.all() for c in contact.contacts.splitlines()]
    messages = campaign.messages.all()
    interval = campaign.send_interval * 60
    max_contacts_per_account = campaign.max_contacts_per_account
    messages_log = []

    for account in accounts:

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        client = create_client(account.phone_number)

        for i, contact_value in enumerate(contacts):
            try:
                for message in messages:
                    try:
                        content_type = message.message_type
                        message_content = message.content
                        media_file = message.media_file

                        loop.run_until_complete(connect_send(client, content_type, contact_value, message_content, media_file))

                        messages_log.append(MessageLog(campaign=campaign, account=account, recipient=contact_value, status='sent'))
                    except Exception as e:
                        error_message = str(e)
                        messages_log.append(MessageLog(campaign=campaign, account=account, recipient=contact_value, status='failed', error_message=error_message, error_detail=traceback.format_exc()))
                        print(f"Error sending message to {contact_value}: {error_message}")

                if (i + 1) % max_contacts_per_account == 0:
                    loop.run_until_complete(asyncio.sleep(interval))
                else:
                    loop.run_until_complete(asyncio.sleep(interval / 2))

            except Exception as e:
                error_message = str(e)
                messages_log.append(MessageLog(campaign=campaign, account=account, recipient=contact_value, status='failed', error_message=error_message, error_detail=traceback.format_exc()))
                print(f"Error sending message to {contact_value}: {error_message}")
                continue
        
        client.disconnect()

    try:
        MessageLog.objects.bulk_create(messages_log)
    except IntegrityError as e:
        print(f"Error saving message logs: {e}")
    campaign.status = 'completed'
    campaign.save()

@async_to_sync
async def test_async():
    print("test_async")
    await asyncio.sleep(5)
    print("test_async end")

@shared_task
def test():
    test_async()

