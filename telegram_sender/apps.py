from django.apps import AppConfig


class TelegramSenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_sender'
    verbose_name = 'Рассылка'
