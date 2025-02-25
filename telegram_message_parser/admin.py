from django.contrib import admin
from django.utils import html
from django.http import HttpResponseRedirect
from django.core.cache import cache

from telegram_message_parser.models import TelegramChannelGroup, KeyWordModel, MessageError
from telegram_message_parser.tasks import parse_message

# Register your models here.

@admin.register(TelegramChannelGroup)
class TelegramChannelGroupAdmin(admin.ModelAdmin):
    fields = ("title", "chat_id", "account", "send_chat_id", "keywords")

    actions = ['parse_messages']

    def parse_messages(self, request, queryset):
        # keywords = KeyWordModel.objects.all()
        # keywords = [line for keyword in keywords for line in keyword.words.splitlines()]
        try:
            for group in queryset:
                keywords = [line for keyword in group.keywords.all() for line in keyword.words.splitlines()]
                parse_message.delay(group.chat_id, group.send_chat_id, str(group.account.phone_number), keywords)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            self.message_user(request, f"Произошла ошибка: {e}")

        self.message_user(request, "Парсинг завершен!")
        return HttpResponseRedirect(request.get_full_path())
    parse_messages.short_description = "Начать парсинг"

@admin.register(KeyWordModel)
class KeyWordAdmin(admin.ModelAdmin):
    pass

# class TelegramMessageImagesInline(admin.StackedInline):
#     model = TelegramMessageImages
#     readonly_fields = ("image_preview",)
#     
#     def image_preview(self, obj):
#         return html.mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')

#     image_preview.short_description = 'Изображение(Предпросмотр)'


# @admin.register(TelegramMessage)
# class TelegramMessageAdmin(admin.ModelAdmin):
#     inlines = [TelegramMessageImagesInline]
#     def has_add_permission(self, request):
#         return False

#     def has_change_permission(self, request, obj=None):
#         return False

#     def has_view_permission(self, request, obj=None):
#         return True


@admin.register(MessageError)
class MessageErrorAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


