from django.contrib import admin
from django.utils import html

from telegram_message_parser.models import TelegramChannelGroup, KeyWordModel, TelegramMessage, TelegramMessageImages

# Register your models here.

@admin.register(TelegramChannelGroup)
class TelegramChannelGroupAdmin(admin.ModelAdmin):
    readonly_fields = ("title", )
    fields = ("title", "chat_id",)


@admin.register(KeyWordModel)
class KeyWordAdmin(admin.ModelAdmin):
    pass

class TelegramMessageImagesInline(admin.StackedInline):
    model = TelegramMessageImages
    readonly_fields = ("image_preview",)
    
    def image_preview(self, obj):
        return html.mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')

    image_preview.short_description = 'Изображение(Предпросмотр)'


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    inlines = [TelegramMessageImagesInline]
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True
