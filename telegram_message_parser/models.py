from django.db import models
from django.core.exceptions import ValidationError

from api.telegram_api import get_chat

# Create your models here.

class TelegramChannelGroup(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название")
    chat_id = models.CharField(max_length=255, unique=True, verbose_name="ID чата")

    def __str__(self) -> str:
        return str(self.title)

    def clean(self):
        success, title = get_chat(str(self.chat_id))
        if not success:
            raise ValidationError("Неверный ID чата")
        self.title = title

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

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


class TelegramMessage(models.Model):
    chat = models.ForeignKey(TelegramChannelGroup, on_delete=models.CASCADE, verbose_name="Канал/Группа")
    sender = models.CharField(max_length=255, verbose_name="Отправитель", null=True, blank=True)
    text = models.TextField(verbose_name="Текст сообщения")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата получения")

    def __str__(self):
        return f"{getattr(self.chat, 'title', 'Нет названия')} - {self.sender or 'Нет отправителя'}"

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class TelegramMessageImages(models.Model):
    message = models.ForeignKey(TelegramMessage, on_delete=models.CASCADE, verbose_name="Сообщение", related_name="images")
    image = models.FileField(verbose_name="Изображение", upload_to="telegram_images/")

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
