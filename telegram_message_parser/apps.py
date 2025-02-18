from django.apps import AppConfig


class TelegramMessageParserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_message_parser'
    verbose_name = 'Телеграм парсер'

    def ready(self):
        import telegram_message_parser.signals
