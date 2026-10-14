from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from orders.emails import send_welcome_email


@receiver(post_save, sender=User)
def user_created_welcome(sender, instance, created, **kwargs):
    """Send a welcome email when a new customer registers."""
    if created and not instance.is_staff and not instance.is_superuser and instance.email:
        send_welcome_email(instance)
