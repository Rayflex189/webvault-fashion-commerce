from django.contrib import admin
from django.utils.html import format_html

from .models import EmailTemplate, EmailCampaign, CampaignLog


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'updated_at')
    search_fields = ('name', 'subject')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Template Info', {
            'fields': ('name', 'subject')
        }),
        ('Body', {
            'fields': ('body_html', 'body_text'),
            'description': (
                "Available variables: <code>{{ customer_name }}</code>, "
                "<code>{{ store_name }}</code>, <code>{{ item_count }}</code>, "
                "<code>{{ subtotal }}</code>, <code>{{ cart_items }}</code>, "
                "<code>{{ recovery_url }}</code>, <code>{{ site_url }}</code>"
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigger', 'delay_hours', 'is_active', 'sent_count', 'last_run_at')
    list_filter = ('trigger', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('sent_count', 'last_run_at', 'created_at', 'updated_at')

    fieldsets = (
        ('Campaign', {
            'fields': ('name', 'trigger', 'delay_hours', 'is_active')
        }),
        ('Email', {
            'fields': ('template',)
        }),
        ('Stats', {
            'fields': ('sent_count', 'last_run_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(CampaignLog)
class CampaignLogAdmin(admin.ModelAdmin):
    list_display = ('sent_at', 'campaign', 'recipient_email', 'subject', 'status_badge')
    list_filter = ('status', 'campaign', 'sent_at')
    search_fields = ('recipient_email', 'subject')
    readonly_fields = ('campaign', 'recipient_email', 'subject', 'status', 'error_message', 'sent_at')

    def status_badge(self, obj):
        if obj.status == 'sent':
            return format_html('<span style="color: green;">✓ Sent</span>')
        return format_html('<span style="color: red;">✗ Failed</span>')
    status_badge.short_description = "Status"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
