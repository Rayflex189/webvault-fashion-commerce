from django.db import models

class DeliveryMethod(models.Model):
    METHOD_TYPES = (
        ('pickup', 'Pickup'),
        ('standard', 'Standard Delivery'),
        ('express', 'Express Delivery'),
        ('in_house', 'In-house Delivery'),
    )

    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    description = models.CharField(max_length=200, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_days = models.CharField(max_length=50, blank=True, help_text="e.g. 2-5 business days")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Display order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.get_method_type_display()})"
