from django.contrib import admin
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import StoreSettings
from products.models import Product
from orders.models import Order
from django.contrib.auth.models import User


# Customize the admin index page
admin.site.index_template = 'admin/custom_index.html'


def custom_index(request, extra_context=None):
    """Custom admin index view that adds business metrics."""
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)

    # Metrics
    today_sales = Order.objects.filter(
        status='paid',
        created_at__date=today
    ).aggregate(total=Sum('total'))['total'] or 0

    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.filter(is_active=True).count()

    # Low stock variants (stock <= 3)
    low_stock = Product.objects.filter(
        is_active=True,
        variants__stock__lte=3
    ).distinct().count()

    total_orders = Order.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()

    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:5]

    extra_context = extra_context or {}
    extra_context.update({
        'today_sales': today_sales,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'low_stock': low_stock,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'currency': StoreSettings.load().currency,
    })
    return admin.site.__class__.index(admin.site, request, extra_context)


# Override the default admin index
admin.site.index = custom_index


# Store Settings admin
@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'contact_email', 'active_gateway', 'currency')

    fieldsets = (
        ('Branding', {
            'fields': ('store_name', 'logo', 'favicon', 'primary_color', 'secondary_color')
        }),
        ('Homepage', {
            'fields': ('hero_text', 'hero_banner', 'about_us')
        }),
        ('Contact Info', {
            'fields': ('contact_email', 'contact_phone', 'whatsapp_number', 'address')
        }),
        ('Business Settings', {
            'fields': ('currency', 'default_delivery_fee')
        }),
        ('Payment Gateway', {
            'fields': ('active_gateway',),
            'description': "Choose which payment gateway to use at checkout. Enter YOUR OWN keys below."
        }),
        ('Paystack Keys', {
            'fields': ('paystack_public_key', 'paystack_secret_key'),
            'classes': ('collapse',),
        }),
        ('Flutterwave Keys', {
            'fields': ('flutterwave_public_key', 'flutterwave_secret_key'),
            'classes': ('collapse',),
        }),
        ('Monnify Keys', {
            'fields': ('monnify_api_key', 'monnify_secret_key', 'monnify_contract_code'),
            'classes': ('collapse',),
        }),
        ('Squad Keys', {
            'fields': ('squad_public_key', 'squad_secret_key'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        return not StoreSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
