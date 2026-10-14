from django.db import models
from django.contrib.auth.models import User


class EmailTemplate(models.Model):
    """Reusable email template the store owner can edit in the admin."""
    name = models.CharField(max_length=100, help_text="Internal name, e.g. 'Cart Reminder v1'")
    subject = models.CharField(max_length=200)
    body_html = models.TextField(
        help_text="HTML body. Use {{ customer_name }}, {{ cart_items }}, {{ store_name }}, {{ recovery_url }}"
    )
    body_text = models.TextField(
        blank=True,
        help_text="Plain text fallback. Leave blank to auto-generate from HTML."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class EmailCampaign(models.Model):
    """
    A campaign defines a rule like:
      'When a cart is abandoned for 4 hours, send Cart Reminder v1'
    """

    TRIGGER_CHOICES = (
        ('cart_abandoned', 'Cart Abandoned'),
        ('user_registered', 'New User Registered'),
        ('order_placed', 'Order Placed (Pending Payment)'),
        ('order_paid', 'Order Paid'),
        ('order_shipped', 'Order Shipped'),
        ('order_delivered', 'Order Delivered'),
        ('customer_lapsed', 'Customer Lapsed (30+ days)'),
    )

    name = models.CharField(max_length=150, help_text="e.g. 'Cart Recovery — 4hr'")
    trigger = models.CharField(max_length=30, choices=TRIGGER_CHOICES)
    delay_hours = models.IntegerField(
        default=4,
        help_text="How long to wait after the trigger before sending (in hours)."
    )
    template = models.ForeignKey(EmailTemplate, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    # Stats
    sent_count = models.IntegerField(default=0, editable=False)
    last_run_at = models.DateTimeField(null=True, blank=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['trigger', 'delay_hours']

    def __str__(self):
        return f"{self.name} ({self.get_trigger_display()})"


class CampaignLog(models.Model):
    """Audit log of every email sent by a campaign."""
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )

    campaign = models.ForeignKey(EmailCampaign, on_delete=models.SET_NULL, null=True, blank=True)
    recipient_email = models.EmailField(db_index=True)
    subject = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.recipient_email} — {self.subject} ({self.status})"
