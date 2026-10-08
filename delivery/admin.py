from django.contrib import admin
from .models import DeliveryMethod

@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'method_type', 'fee', 'estimated_days', 'is_active', 'order')
    list_editable = ('is_active', 'fee', 'order')
