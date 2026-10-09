from django.db import models


class StoreSettings(models.Model):
    """
    Singleton model that holds all configurable settings for a store instance.
    Each buyer customizes THIS instead of editing code.
    """

    PAYMENT_GATEWAY_CHOICES = (
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('monnify', 'Monnify'),
        ('squad', 'Squad'),
        ('none', 'No Online Payment (Cash/Transfer only)'),
    )

    # ─────────────────────────────────────────
    # BRANDING
    # ─────────────────────────────────────────
    store_name = models.CharField(max_length=200, default="WebVault Fashion Store")
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    favicon = models.ImageField(upload_to='branding/', blank=True, null=True)
    primary_color = models.CharField(
        max_length=7, default="#4F46E5",
        help_text="Hex code e.g. #4F46E5"
    )
    secondary_color = models.CharField(
        max_length=7, default="#1E293B",
        help_text="Hex code e.g. #1E293B"
    )

    # ─────────────────────────────────────────
    # HOMEPAGE
    # ─────────────────────────────────────────
    hero_text = models.CharField(max_length=200, default="Elegance in Every Stitch")
    hero_banner = models.ImageField(upload_to='branding/', blank=True, null=True)
    about_us = models.TextField(blank=True)

    # ─────────────────────────────────────────
    # CONTACT INFO
    # ─────────────────────────────────────────
    contact_email = models.EmailField(default="hello@example.com")
    contact_phone = models.CharField(max_length=20, blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # ─────────────────────────────────────────
    # BUSINESS SETTINGS
    # ─────────────────────────────────────────
    currency = models.CharField(max_length=3, default="NGN")
    default_delivery_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=3000.00
    )

    # ─────────────────────────────────────────
    # PAYMENT GATEWAY CONFIGURATION
    # ─────────────────────────────────────────
    active_gateway = models.CharField(
        max_length=20,
        choices=PAYMENT_GATEWAY_CHOICES,
        default='paystack',
        help_text="Which payment gateway to use at checkout"
    )

    # Paystack Keys
    paystack_public_key = models.CharField(max_length=200, blank=True)
    paystack_secret_key = models.CharField(max_length=200, blank=True)

    # Flutterwave Keys
    flutterwave_public_key = models.CharField(max_length=200, blank=True)
    flutterwave_secret_key = models.CharField(max_length=200, blank=True)

    # Monnify Keys
    monnify_api_key = models.CharField(max_length=200, blank=True)
    monnify_secret_key = models.CharField(max_length=200, blank=True)
    monnify_contract_code = models.CharField(max_length=200, blank=True)

    # Squad Keys
    squad_public_key = models.CharField(max_length=200, blank=True)
    squad_secret_key = models.CharField(max_length=200, blank=True)

    # ─────────────────────────────────────────
    # META
    # ─────────────────────────────────────────
    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        # Force pk=1 so only one settings record can ever exist (Singleton pattern)
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Convenience method: fetch the single settings instance (create if missing)."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    # ─────────────────────────────────────────
    # HELPER PROPERTIES (used in templates and views)
    # ─────────────────────────────────────────
    @property
    def is_payment_enabled(self):
        """True if the store has an active online payment gateway configured."""
        if self.active_gateway == 'none':
            return False
        # Check that the relevant keys are present
        if self.active_gateway == 'paystack':
            return bool(self.paystack_secret_key)
        if self.active_gateway == 'flutterwave':
            return bool(self.flutterwave_secret_key)
        if self.active_gateway == 'monnify':
            return bool(self.monnify_secret_key)
        if self.active_gateway == 'squad':
            return bool(self.squad_secret_key)
        return False

    @property
    def active_public_key(self):
        """Return the public key of the currently active gateway (for frontend use)."""
        keys = {
            'paystack': self.paystack_public_key,
            'flutterwave': self.flutterwave_public_key,
            'monnify': self.monnify_api_key,
            'squad': self.squad_public_key,
        }
        return keys.get(self.active_gateway, '')
