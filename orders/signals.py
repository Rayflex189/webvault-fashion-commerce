from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Order
from . import emails


@receiver(pre_save, sender=Order)
def order_status_tracking(sender, instance, **kwargs):
    """Store the previous status on the instance so post_save can compare."""
    if instance.pk:
        try:
            old_order = Order.objects.get(pk=instance.pk)
            instance._previous_status = old_order.status
        except Order.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    """Fire appropriate emails when an order is created or its status changes."""
    store = None
    try:
        from core.models import StoreSettings
        store = StoreSettings.load()
    except Exception:
        pass

    # New order created
    if created:
        emails.send_order_placed_email(instance)
        return

    previous = getattr(instance, '_previous_status', None)

    # No status change → nothing to do
    if previous == instance.status:
        return

    # Status → paid
    if instance.status == 'paid':
        emails.send_payment_confirmed_email(instance)
        emails.send_new_sale_email_to_seller(instance)

    # Status → shipped
    elif instance.status == 'shipped':
        emails.send_order_shipped_email(instance)

    # Status → delivered
    elif instance.status == 'delivered':
        emails.send_order_delivered_email(instance)
