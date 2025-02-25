from django.db import models

from telegram_sender.models import TelegramAccount

# Create your models here.


class KeyWordModel(models.Model):
    words = models.TextField(verbose_name="Ключевые слова")

    def __str__(self) -> str:
        return f"Ключевые слова {self.pk}"

    class Meta:
        verbose_name = 'Ключевое слово'
        verbose_name_plural = 'Ключевые слова'


class TelegramChannelGroup(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название")
    chat_id = models.TextField(verbose_name="ID чата/канала")
    account = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE, verbose_name="Аккаунт")
    keywords = models.ManyToManyField(KeyWordModel, verbose_name="Ключевые слова")
    send_chat_id = models.TextField(verbose_name="ID чата для отправки")

    def __str__(self) -> str:
        return f"{self.title or 'Нет названия'} - {self.chat_id} - {self.send_chat_id}"

    class Meta:
        verbose_name = 'Канал/Группа'
        verbose_name_plural = 'Каналы/Группы'


class MessageError(models.Model):
    channel = models.CharField(max_length=255, verbose_name="Канал/Группа")
    error = models.TextField(verbose_name="Текст ошибки", null=True, blank=True)
    error_detail = models.TextField(verbose_name="Детали ошибки", null=True, blank=True)

    class Meta:
        verbose_name = 'Ошибка'
        verbose_name_plural = 'Ошибки'
