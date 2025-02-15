from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group

from telegram_sender.models import Campaign, TelegramAccount, PreparedMessage, Contact, MessageLog
from telegram_sender.tasks import send_campaign_messages, test, send_campaign_messages_in_thread
from telegram_sender.forms import TelegramAccountForm

from asgiref.sync import async_to_sync

from threading import Thread

# Register your models here.



@admin.register(TelegramAccount)
class TelegramAccountAdmin(admin.ModelAdmin):
    form = TelegramAccountForm
    list_display = ('session_name', 'phone_number', 'is_active',)

 
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_value', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(PreparedMessage)
class PreparedMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'message_type', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'status', 'timestamp')
    readonly_fields = ('timestamp', 'campaign', 'account', 'recipient', 'status', 'error_message')

    def has_add_permission(self, request):
        return False


class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'send_interval', 'max_contacts_per_account', 'created_at')
    readonly_fields = ('status',)
    search_fields = ('name',)
    list_filter = ('status',)

    actions = ['start_campaign']

    def start_campaign(self, request, queryset):
        try:
            for campaign in queryset:
                send_campaign_messages.delay(campaign.id)
                # thread = Thread(target=send_campaign_messages_in_thread, args=(campaign.id,))
                # thread = Thread(target=send_campaign_messages, args=(campaign.id,))
                # thread.start()
                # send_campaign_messages.delay(campaign.id)
                # test()
        except Exception as e:
            self.message_user(request, f"Произошла ошибка: {e}")

        self.message_user(request, "Рассылка запущена!")
        return HttpResponseRedirect(request.get_full_path())
    start_campaign.short_description = "Запустить рассылку"

admin.site.register(Campaign, CampaignAdmin)
admin.site.unregister(Group)
