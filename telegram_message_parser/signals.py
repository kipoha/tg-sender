from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.cache import cache

from telegram_message_parser.models import TelegramChannelGroup, KeyWordModel


@receiver(post_save, sender=TelegramChannelGroup)
def add_all(sender, instance, **kwargs):
    print("start group")
    data = list(sender.objects.values_list("chat_id", flat=True))
    cache.set('all_channels', data)
    print(cache.get('all_channels'))


@receiver(post_save, sender=KeyWordModel)
def add_all_keywords(sender, instance, **kwargs):
    print("start keywords")
    data = list(sender.objects.values_list("word", flat=True))
    cache.set('all_keywords', data)
    print(cache.get('all_keywords'))
