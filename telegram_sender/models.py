from django.db import models
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class TelegramAccount(models.Model):
    session_name = models.CharField(max_length=255, unique=True, verbose_name="Название сессии")
    phone_number = PhoneNumberField(unique=True, verbose_name="Номер телефона")
    is_active = models.BooleanField(default=False, verbose_name="Активен", editable=False)

    def __str__(self):
        return f"{self.phone_number} ({'Активен' if self.is_active else 'Неактивен'})"

    class Meta:
        verbose_name = "Telegram аккаунт"
        verbose_name_plural = "Telegram аккаунты"

class Contact(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    contacts = models.TextField(verbose_name="Список номеров и никнеймов")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"


class PreparedMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Текст'),
        ('photo', 'Фото'),
        ('video', 'Видео'),
        ('voice', 'Голосовое сообщение'),
        ('round', 'Видеокружок')
    )
    
    name = models.CharField(max_length=255, verbose_name="Название сообщения")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, verbose_name="Тип сообщения")
    content = models.TextField(blank=True, null=True, verbose_name="Текст сообщения")
    media_file = models.FileField(upload_to='messages/', blank=True, null=True, verbose_name="Медиафайл")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.message_type == 'text':
            if not self.content and self.media_file:
                raise ValidationError({"content": "Текстовое сообщение должно содержать текст",
                                       "media_file": "Медиафайл не может присутствовать для текстового сообщения"})
        elif self.message_type in ['photo', 'video', 'voice', 'round'] and not self.media_file:
            raise ValidationError({"media_file": "Медиафайл не может быть пустым"})

        if self.media_file:
            file_extension = self.media_file.name.split('.')[-1]
            allowed_extensions = {
                'photo': ['jpg', 'png', 'gif', 'jpeg', 'webp'],
                'video': ['mp4', 'avi', 'mov'],
                'voice': ['mp3', 'wav', 'ogg', 'acc'],
                'round': ['mp4', 'mov', 'avi']
            }

            if file_extension not in allowed_extensions.get(self.message_type, []):
                raise ValidationError({
                    "media_file": f"Неверный формат файла для типа {self.get_message_type_display()} (допустимые форматы: {', '.join(allowed_extensions.get(self.message_type, []))})."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Заготовленное сообщение"
        verbose_name_plural = "Заготовленные сообщения"

class Campaign(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название рассылки")
    contacts = models.ManyToManyField(Contact, verbose_name="Контакты")
    messages = models.ManyToManyField(PreparedMessage, verbose_name="Шаблон сообщения")
    accounts = models.ManyToManyField(TelegramAccount, verbose_name="Аккаунты")
    send_interval = models.IntegerField(default=5, verbose_name="Интервал отправки(в минутах)")
    max_contacts_per_account = models.IntegerField(default=10, verbose_name="Максимальное количество контактов в аккаунте")
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Ожидает'), ('running', 'Запущена'), ('completed', 'Завершена')],
        default='pending',
        verbose_name="Статус рассылки"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

class MessageLog(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, verbose_name="Рассылка")
    account = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE, verbose_name="Аккаунт")
    recipient = models.CharField(max_length=255)
    status = models.CharField( max_length=10,
        choices=[('sent', 'Отправлен'), ('failed', 'Ошибка')],
        default='sent'
    )
    error_message = models.TextField(blank=True, null=True, verbose_name="Сообщение об ошибке")
    error_detail = models.TextField(blank=True, null=True, verbose_name="Детали ошибки")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient} - {self.status}"

    class Meta:
        verbose_name = "Лог сообщений"
        verbose_name_plural = "Логи сообщений"
