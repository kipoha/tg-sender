import asyncio

from asgiref.sync import sync_to_async, async_to_sync

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
                # Логирование ошибок
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

def send_campaign_messages_in_thread(campaign_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Запуск задач в отдельном потоке
        loop.run_until_complete(send_campaign_messages(campaign_id))
    except Exception as e:
        print(f"Error in send_campaign_messages_in_thread: {e}")
    finally:
        loop.close()


@async_to_sync
async def test_async():
    print("test_async")
    await asyncio.sleep(5)
    print("test_async end")

@shared_task
def test():
    test_async()


# async def connect_send(client: TelegramClient, content_type, contact_value, message_content=None, media_file=None):
#     if not client.is_connected():
#         await client.connect()

#     if content_type == 'text':
#         await client.send_message(contact_value, message_content)
#     elif content_type in ['photo', 'video', 'voice', 'round']:
#         await client.send_file(contact_value, media_file, caption=message_content)


# @shared_task
# def send_campaign_messages(campaign_id):
#     campaign = Campaign.objects.get(pk=campaign_id)
#     accounts = campaign.accounts.all()
#     contacts = campaign.contacts.all()
#     interval = campaign.send_interval * 60
#     max_contacts_per_account = campaign.max_contacts_per_account
#     messages_log = []
#     for account in accounts:
#         client = TelegramClient(str(account.phone_number), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)


#         for i, contact in enumerate(contacts):
#             try:
#                 content_type = campaign.message.message_type
#                 message_content = campaign.message.content
#                 contact_value = contact.contact_value
#                 media_file = campaign.message.media_file

#                 async_to_sync(connect_send)(client, content_type, contact_value, message_content, media_file)

#                 messages_log.append(MessageLog(campaign=campaign, account=account, recipient=contact_value, status='sent'))

#                 if (i + 1) % max_contacts_per_account == 0:
#                     async_to_sync(asyncio.sleep)(interval)
#                 else:
#                     async_to_sync(asyncio.sleep)(interval / 2)

#             except Exception:
#                 import traceback
#                 e = traceback.format_exc()
#                 contact_value = contact.contact_value
#                 messages_log.append(MessageLog(campaign=campaign, account=account, recipient=contact_value, status='failed', error_message=str(e)))
#         if client.is_connected():
#             client.disconnect()

#     MessageLog.objects.bulk_create(messages_log)



# def send_campaign_messages_in_thread(campaign_id):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(send_campaign_messages(campaign_id))


# @sync_to_async
# def get_campaign(campaign_id):
#     return Campaign.objects.get(pk=campaign_id)

# @sync_to_async
# def get_accounts(campaign):
#     return campaign.accounts.all()

# @sync_to_async
# def get_contacts(campaign):
#     return campaign.contacts.all()

# @sync_to_async
# def create_message_log(array):
#     MessageLog.objects.bulk_create(array)

# @sync_to_async
# def get_client(account):
#     return TelegramClient(str(account.phone_number), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)

# @sync_to_async
# def get_message_type_and_message_content(campaign):
#     return campaign.message.message_type, campaign.message.content

# @sync_to_async
# def get_contact_value(contact):
#     return contact.contact_value

# @sync_to_async
# def get_media_file(campaign):
#     return campaign.message.media_file

# @sync_to_async
# def add_to_message_log(messages_log, campaign, account, recipient, status, error_message=None):
#     messages_log.append(MessageLog(campaign=campaign, account=account, recipient=recipient, status=status, error_message=error_message))

# @sync_to_async
# def disconnect(client):
#     client.disconnect()

# @sync_to_async
# def create_traceback():
#     import traceback
#     return traceback.format_exc()

# @shared_task
# def send_campaign_messages(campaign_id):
#     # Используем async_to_sync для того, чтобы запускать async функцию из Celery task.
#     async_to_sync(async_send_campaign_messages)(campaign_id)

# async def async_send_campaign_messages(campaign_id):
#     campaign = await get_campaign(campaign_id)
#     accounts = await get_accounts(campaign)
#     contacts = await get_contacts(campaign)
#     interval = campaign.send_interval * 60
#     max_contacts_per_account = campaign.max_contacts_per_account
#     messages_log = []

#     async def send_with_account(account):
#         client = await get_client(account)
#         await client.connect()
#         for i, contact in enumerate(contacts):
#             try:
#                 content_type, message_content = await get_message_type_and_message_content(campaign)
#                 contact_value = await get_contact_value(contact)
#                 if content_type == 'text':
#                     await client.send_message(contact_value, message_content)
#                 elif content_type in ['photo', 'video', 'voice', 'round']:
#                     media_file = await get_media_file(campaign)
#                     await client.send_file(contact_value, media_file, caption=message_content)

#                 await add_to_message_log(messages_log, campaign, account, contact_value, 'sent')

#                 if (i + 1) % max_contacts_per_account == 0:
#                     await asyncio.sleep(interval)
#                 else:
#                     await asyncio.sleep(interval / 2)

#             except Exception:
#                 e = await create_traceback()
#                 contact_value = await get_contact_value(contact)
#                 await add_to_message_log(messages_log, campaign, account, contact_value, 'failed', e)

#         await disconnect(client)

#     tasks = [send_with_account(account) for account in accounts]
#     await asyncio.gather(*tasks)

#     await create_message_log(messages_log)










# @sync_to_async
# def get_campaign(campaign_id):
#     return Campaign.objects.get(pk=campaign_id)

# @sync_to_async
# def get_accounts(campaign):
#     return campaign.accounts.all()

# @sync_to_async
# def get_contacts(campaign):
#     return campaign.contacts.all()

# @sync_to_async
# def create_message_log(array):
#     MessageLog.objects.bulk_create(array)

# @sync_to_async
# def get_client(account):
#     return TelegramClient(str(account.phone_number), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)

# @sync_to_async
# def get_message_type_and_message_content(campaign):
#     return campaign.message.message_type, campaign.message.content

# @sync_to_async
# def get_contact_value(contact):
#     return contact.contact_value

# @sync_to_async
# def get_media_file(campaign):
#     return campaign.message.media_file

# @sync_to_async
# def add_to_message_log(messages_log, campaign, account, recipient, status, error_message=None):
#     messages_log.append(MessageLog(campaign=campaign, account=account, recipient=recipient, status=status, error_message=error_message))

# @sync_to_async
# def disconnect(client):
#     client.disconnect()

# @sync_to_async
# def create_traceback():
#     import traceback
#     return traceback.format_exc()


# @shared_task
# def send_campaign_messages(campaign_id):
#     asyncio.run(async_send_campaign_messages(campaign_id))

# async def async_send_campaign_messages(campaign_id):
#     campaign = await get_campaign(campaign_id)
#     accounts = await get_accounts(campaign)
#     contacts = await get_contacts(campaign)
#     interval = campaign.send_interval * 60
#     max_contacts_per_account = campaign.max_contacts_per_account
#     messages_log = []

#     async def send_with_account(account):
#         client = await get_client(account)
#         await client.connect()
#         for i, contact in enumerate(contacts):
#             try:
#                 content_type, message_content = await get_message_type_and_message_content(campaign)
#                 contact_value = await get_contact_value(contact)
#                 if content_type == 'text':
#                     await client.send_message(contact_value, message_content)
#                 elif content_type in ['photo', 'video', 'voice', 'round']:
#                     media_file = await get_media_file(campaign)
#                     await client.send_file(contact_value, media_file, caption=message_content)

#                 await add_to_message_log(messages_log, campaign, account, contact_value, 'sent')

#                 if (i + 1) % max_contacts_per_account == 0:
#                     await asyncio.sleep(interval)
#                 else:
#                     await asyncio.sleep(interval / 2)

#             except Exception:
#                 e = await create_traceback()
#                 contact_value = await get_contact_value(contact)
#                 await add_to_message_log(messages_log, campaign, account, contact_value, 'failed', e)

#         await disconnect(client)

#     tasks = [send_with_account(account) for account in accounts]
#     await asyncio.gather(*tasks)

#     await create_message_log(messages_log)















# @shared_task
# def send_campaign_messages(campaign_id):
#     campaign = Campaign.objects.get(pk=campaign_id)
#     accounts = campaign.accounts.all()
#     contacts = campaign.contacts.all()
#     interval = campaign.send_interval * 60
#     max_contacts_per_account = campaign.max_contacts_per_account
#     messages_log = []
#     for account in accounts:
#         client = TelegramClient(str(account.phone_number), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)
#         async_to_sync(client.connect)
#         for i, contact in enumerate(contacts):
#             try:
#                 content_type = campaign.message.message_type
#                 message_content = campaign.message.content
#                 contact_value = contact.contact_value
#                 if content_type == 'text':
#                     async_to_sync(client.send_message)(contact_value, message_content)
#                 elif content_type in ['photo', 'video', 'voice', 'round']:
#                     media_file = campaign.message.media_file
#                     async_to_sync(client.send_file)(contact_value, media_file, caption=message_content)

#                 messages_log.append(MessageLog(campaign=campaign, account=account, recipient=contact_value, status='sent'))

#                 if (i + 1) % max_contacts_per_account == 0:
#                     time.sleep(interval)
#                 else:
#                     time.sleep(interval / 2)

#             except Exception:
#                 import traceback
#                 e = traceback.format_exc()
#                 contact_value = contact.contact_value
#                 messages_log.append(MessageLog(campaign=campaign, account=account, recipient=contact_value, status='failed', error_message=str(e)))

#     client.disconnect()

#     MessageLog.objects.bulk_create(messages_log)

# #             async with TelegramClient(str(phone_number), api_id, api_hash) as client:
#                 for i, contact in enumerate(contacts):
#                     try:
#                         content_type = await get_content_type(campaign)
#                         message_content = await get_campaign_message_content(campaign)
#                         contact_value = await get_contact_value(contact)
#                         if content_type == 'text':
#                             await client.send_message(contact_value, message_content)
#                         elif content_type in ['photo', 'video', 'voice', 'round']:
#                             media_file = await get_media_file(campaign)
#                             await client.send_file(contact_value, media_file, caption=message_content)

#                         await create_message_log(campaign, account, contact_value, 'sent')

#                         if (i + 1) % max_contacts_per_account == 0:
#                             await asyncio.sleep(interval)
#                         else:
#                             await asyncio.sleep(interval / 2)

#                     except Exception:
#                         import traceback
#                         e = traceback.format_exc()
#                         contact_value = await get_contact_value(contact)
#                         await create_message_log(campaign, account, contact_value, 'failed', str(e))
#






















# import asyncio

# from celery import shared_task

# from telethon import TelegramClient

# from telegram_sender.models import Campaign, MessageLog

# from asgiref.sync import sync_to_async, async_to_sync

# from django.conf import settings

# @sync_to_async
# def create_message_log(campaign, account, recipient, status, error_message=None):
#     MessageLog.objects.create(
#         campaign=campaign,
#         account=account,
#         recipient=recipient,
#         status=status,
#         error_message=error_message
#     )

# @sync_to_async
# def complete_campaign(campaign):
#     campaign.status = 'completed'
#     campaign.save()

# @sync_to_async
# def get_campaign_message_content(campaign):
#     return campaign.message.content

# @sync_to_async
# def get_content_type(campaign):
#     return campaign.message.message_type

# @sync_to_async
# def get_media_file(campaign):
#     return campaign.message.media_file

# @sync_to_async
# def get_campaign(pk):
#     return Campaign.objects.get(pk=pk)

# @sync_to_async
# def get_campaign_accounts(campaign):
#     return campaign.accounts.all()

# @sync_to_async
# def get_campaign_contacts(campaign):
#     return campaign.contacts.all()

# @sync_to_async
# def get_contact_value(contact):
#     return contact.contact_value

# @sync_to_async
# def get_semaphore(limit):
#     return asyncio.Semaphore(limit)

# @sync_to_async
# def get_interval(campaign):
#     return campaign.send_interval * 60

# @sync_to_async
# def get_max_contacts_per_account(campaign):
#     return campaign.max_contacts_per_account

# @sync_to_async
# def get_account_phone_number(account):
#     return account.phone_number

# @shared_task
# def send_campaign_messages(campaign_id):
#     campaign: Campaign = Campaign.objects.get(pk=campaign_id)
#     accounts = campaign.accounts.all()
#     contacts = campaign.contacts.all()
#     interval = campaign.send_interval * 60
#     max_contacts_per_account = campaign.max_contacts_per_account

#     async_to_sync(send_messages)(campaign, accounts, contacts, interval, max_contacts_per_account, settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)

# async def send_messages(campaign, accounts, contacts, interval, max_contacts_per_account, api_id, api_hash):
#     semaphore = await get_semaphore(3)

#     async def send_with_account(account):
#         async with semaphore:
#             phone_number = await get_account_phone_number(account)
#             async with TelegramClient(str(phone_number), api_id, api_hash) as client:
#                 for i, contact in enumerate(contacts):
#                     try:
#                         content_type = await get_content_type(campaign)
#                         message_content = await get_campaign_message_content(campaign)
#                         contact_value = await get_contact_value(contact)
#                         if content_type == 'text':
#                             await client.send_message(contact_value, message_content)
#                         elif content_type in ['photo', 'video', 'voice', 'round']:
#                             media_file = await get_media_file(campaign)
#                             await client.send_file(contact_value, media_file, caption=message_content)

#                         await create_message_log(campaign, account, contact_value, 'sent')

#                         if (i + 1) % max_contacts_per_account == 0:
#                             await asyncio.sleep(interval)
#                         else:
#                             await asyncio.sleep(interval / 2)

#                     except Exception:
#                         import traceback
#                         e = traceback.format_exc()
#                         contact_value = await get_contact_value(contact)
#                         await create_message_log(campaign, account, contact_value, 'failed', str(e))
#                         

#     tasks = [send_with_account(account) for account in accounts]
#     await asyncio.gather(*tasks)

#     await complete_campaign(campaign)

