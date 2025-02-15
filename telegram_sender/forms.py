from asgiref.sync import async_to_sync

from django import forms
from django.conf import settings
from django.core.cache import cache

from telegram_sender.models import TelegramAccount
from telegram_sender.utils import create_client

from telethon import TelegramClient
from telethon.errors import PhoneCodeInvalidError, SessionPasswordNeededError, PhoneCodeExpiredError, PhoneCodeEmptyError

async def verify_telegram_code(phone_number, code) -> tuple[bool, str]:
    """Подтверждает код и сохраняет сессию"""
    client = create_client(phone_number)

    await client.connect()
    if not await client.is_user_authorized():
        try:
            phone_code_hash = cache.get(phone_number)
            if not phone_code_hash:
                print("❌ Не найден phone_code_hash")
                return False, "Не найден phone_code_hash"

            await client.sign_in(phone_number, code, phone_code_hash=phone_code_hash)
            print(f"✅ Успешная авторизация для {phone_number}")
            client.disconnect()
            return True, "Успешная авторизация"
        except PhoneCodeInvalidError:
            print("❌ Неверный код!")
            client.disconnect()
            return False, "Неверный код!"
        except SessionPasswordNeededError:
            print("⚠️ Требуется двухфакторный пароль!")
            client.disconnect()
            return False, "Требуется двухфакторный пароль!"
        except PhoneCodeExpiredError:
            print("❌ Код истек!")
            client.disconnect()
            return False, "Код истек! Чтобы получить новый, сохраните аккаунт без кода."
    else:
        print("✅ Уже авторизован!")
        client.disconnect()
        return True, "Уже авторизован!"


async def send_telegram_code(phone_number):
    """Отправляет код подтверждения и сохраняет phone_code_hash"""
    client = TelegramClient(str(phone_number), settings.TELEGRAM_API_ID, settings.TELEGRAM_API_HASH)

    await client.connect()
    if not await client.is_user_authorized():
        sent_code = await client.send_code_request(phone_number)
        cache.set(phone_number, sent_code.phone_code_hash, 300)
        print(f"📲 Код подтверждения отправлен на {phone_number}")
        client.disconnect()
        return sent_code.phone_code_hash



class TelegramAccountForm(forms.ModelForm):
    code = forms.CharField(label="Введите код подтверждения", max_length=10, required=False)

    class Meta:
        model = TelegramAccount
        fields = ["phone_number", "session_name", "code"]

    def clean_code(self):
        code = self.cleaned_data.get("code")
        phone_number = self.cleaned_data.get("phone_number")
        if not code:
            hash_ = async_to_sync(send_telegram_code)(phone_number)
            if not hash_:
                self.add_error("code", "Не удалось отправить код подтверждения")
        elif code:
            success, message = async_to_sync(verify_telegram_code)(phone_number, code)
            if not success:
                self.add_error("code", message)

        return code

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


