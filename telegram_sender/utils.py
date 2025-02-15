import os

from telethon import TelegramClient
from telethon.sessions import SQLiteSession

from django.conf import settings

def create_client(phone_number) -> TelegramClient:
    session_dir = os.path.join(settings.BASE_DIR, 'sessions')
    os.makedirs(session_dir, exist_ok=True)

    session_path = os.path.join(session_dir, f'{phone_number}.session')

    return TelegramClient(
        SQLiteSession(session_path),
        settings.TELEGRAM_API_ID,
        settings.TELEGRAM_API_HASH
    )
