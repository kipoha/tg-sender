from django.db import models

from telegram_sender.models import TelegramAccount

# Create your models here.

class TelegramChannelGroup(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название")
    chat_id = models.TextField(verbose_name="ID чата/канала")
    account = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE, verbose_name="Аккаунт")
    send_chat_id = models.TextField(verbose_name="ID чата для отправки")

    def __str__(self) -> str:
        return f"{self.title or 'Нет названия'} - {self.chat_id} - {self.send_chat_id}"

    class Meta:
        verbose_name = 'Канал/Группа'
        verbose_name_plural = 'Каналы/Группы'


class KeyWordModel(models.Model):
    word = models.CharField(max_length=255, verbose_name="Ключевое слово")

    def __str__(self) -> str:
        return str(self.word)

    class Meta:
        verbose_name = 'Ключевое слово'
        verbose_name_plural = 'Ключевые слова'


# class TelegramMessage(models.Model):
#     chat = models.ForeignKey(TelegramChannelGroup, on_delete=models.CASCADE, verbose_name="Канал/Группа")
#     sender = models.CharField(max_length=255, verbose_name="Отправитель", null=True, blank=True)
#     text = models.TextField(verbose_name="Текст сообщения")
#     date = models.DateTimeField(auto_now_add=True, verbose_name="Дата получения")

#     def __str__(self):
#         return f"{getattr(self.chat, 'title', 'Нет названия')} - {self.sender or 'Нет отправителя'} - {self.pk}"

#     class Meta:
#         verbose_name = 'Сообщение'
#         verbose_name_plural = 'Сообщения'


# class TelegramMessageImages(models.Model):
#     message = models.ForeignKey(TelegramMessage, on_delete=models.CASCADE, verbose_name="Сообщение", related_name="images")
#     image = models.FileField(verbose_name="Изображение", upload_to="telegram_images/")

#     class Meta:
#         verbose_name = 'Изображение'
#         verbose_name_plural = 'Изображения'


class MessageError(models.Model):
    channel = models.ForeignKey(TelegramChannelGroup, on_delete=models.CASCADE, verbose_name="Канал/Группа", null=True, blank=True)
    error = models.TextField(verbose_name="Текст ошибки", null=True, blank=True)
    error_detail = models.TextField(verbose_name="Детали ошибки", null=True, blank=True)

    class Meta:
        verbose_name = 'Ошибка'
        verbose_name_plural = 'Ошибки'
