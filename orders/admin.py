from django.contrib import admin
from .models import Order, OrderItem, AbandonedCart


@admin.register(AbandonedCart)
class AbandonedCartAdmin(admin.ModelAdmin):
    list_display = ('session_key_short', 'email', 'item_count', 'subtotal',
                    'is_converted', 'reminder_sent', 'updated_at')
    list_filter = ('is_converted', 'reminder_sent', 'updated_at')
    search_fields = ('email', 'session_key')
    readonly_fields = ('session_key', 'created_at', 'updated_at', 'reminder_sent_at')

    def session_key_short(self, obj):
        return obj.session_key[:12] + '...'
    session_key_short.short_description = 'Session'

    actions = ['send_reminder_now']

    @admin.action(description="Send reminder email now")
    def send_reminder_now(self, request, queryset):
        from orders.emails import send_abandoned_cart_email
        sent = 0
        for cart in queryset.filter(is_converted=False, reminder_sent=False):
            if cart.email or (cart.user and cart.user.email):
                if not cart.email and cart.user:
                    cart.email = cart.user.email
                    cart.save(update_fields=['email'])
                send_abandoned_cart_email(cart, [])
                sent += 1
        self.message_user(request, f"{sent} reminder(s) sent.")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'size_name', 'color_name', 'price', 'quantity')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'email', 'full_name')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')
