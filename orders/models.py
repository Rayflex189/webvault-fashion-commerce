import uuid
from django.db import models
from django.contrib.auth.models import User
from products.models import ProductVariant
from delivery.models import DeliveryMethod

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    order_number = models.CharField(max_length=20, unique=True, blank=True)
    
    # Customer info
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)

    # Delivery
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.SET_NULL, null=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='NGN')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)

    # Ownership (optional — allows guest checkout)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"WV{str(uuid.uuid4().int)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True)
    
    # Snapshot of product data at time of purchase
    product_name = models.CharField(max_length=200)
    size_name = models.CharField(max_length=20)
    color_name = models.CharField(max_length=50)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)

    @property
    def line_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
