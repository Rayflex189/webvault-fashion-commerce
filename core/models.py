from django.db import models

class StoreSettings(models.Model):
    store_name = models.CharField(max_length=200, default="WebVault Fashion Store")
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#4F46E5", help_text="Hex code e.g. #4F46E5")
    secondary_color = models.CharField(max_length=7, default="#1E293B", help_text="Hex code e.g. #1E293B")
    hero_text = models.CharField(max_length=200, default="Elegance in Every Stitch")
    hero_banner = models.ImageField(upload_to='branding/', blank=True, null=True)
    about_us = models.TextField(blank=True)
    contact_email = models.EmailField(default="hello@example.com")
    contact_phone = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default="NGN")
    default_delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=3000.00)

    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        # Ensure only one instance of StoreSettings exists
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
