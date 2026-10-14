from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

from core.models import StoreSettings


def _get_site_url():
    """
    Return the site's base URL for building absolute links in emails.
    In production, set SITE_URL as an env var (e.g. https://mystore.com).
    """
    return getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')


def _send_email(subject, template_name, context, to_email):
    """Helper to send HTML emails with plain-text fallback."""
    if not to_email:
        return False

    store = StoreSettings.load()

    # Make a copy so we don't mutate the caller's dict
    context = dict(context or {})

    # Always inject store + site_url so templates don't need the request object
    context.update({
        'store': store,
        'site_url': _get_site_url(),
    })

    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    from_email = f"{store.store_name} <{settings.DEFAULT_FROM_EMAIL}>"

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email],
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        # Never crash the request if email fails
        import logging
        logging.getLogger(__name__).warning(f"Email send failed: {e}")
        return False


# ─────────────────────────────────────────
# CUSTOMER EMAILS
# ─────────────────────────────────────────

def send_order_placed_email(order):
    subject = f"Order {order.order_number} Received — {StoreSettings.load().store_name}"
    _send_email(
        subject=subject,
        template_name='emails/order_placed.html',
        context={'order': order},
        to_email=order.email,
    )


def send_payment_confirmed_email(order):
    subject = f"Payment Confirmed — Order {order.order_number}"
    _send_email(
        subject=subject,
        template_name='emails/payment_confirmed.html',
        context={'order': order},
        to_email=order.email,
    )


def send_order_shipped_email(order):
    subject = f"Your Order {order.order_number} is on the way!"
    _send_email(
        subject=subject,
        template_name='emails/order_shipped.html',
        context={'order': order},
        to_email=order.email,
    )


def send_order_delivered_email(order):
    subject = f"Order {order.order_number} Delivered"
    _send_email(
        subject=subject,
        template_name='emails/order_delivered.html',
        context={'order': order},
        to_email=order.email,
    )


# ─────────────────────────────────────────
# SELLER EMAILS
# ─────────────────────────────────────────

def send_new_sale_email_to_seller(order):
    store = StoreSettings.load()
    subject = f"🎉 New Sale! Order {order.order_number} — {order.currency} {order.total}"
    _send_email(
        subject=subject,
        template_name='emails/new_sale_seller.html',
        context={'order': order},
        to_email=store.contact_email,
    )


# ─────────────────────────────────────────
# WELCOME EMAIL (Cycle 1)
# ─────────────────────────────────────────

def send_welcome_email(user):
    """Fired automatically when a new customer registers."""
    if not user.email:
        return False

    store = StoreSettings.load()
    subject = f"Welcome to {store.store_name}!"

    return _send_email(
        subject=subject,
        template_name='emails/welcome.html',
        context={'customer': user},
        to_email=user.email,
    )


# ─────────────────────────────────────────
# ABANDONED CART RECOVERY (Cycle 1)
# ─────────────────────────────────────────

def send_abandoned_cart_email(abandoned_cart, cart_items=None):
    """
    Send an abandoned cart reminder.

    `cart_items` is optional. For Cycle 1, we only need the snapshot fields
    (item_count, subtotal). Cycle 2 will pass actual line items.
    """
    email = abandoned_cart.email or (abandoned_cart.user.email if abandoned_cart.user else '')
    if not email:
        return False

    store = StoreSettings.load()
    subject = f"You left something behind at {store.store_name}"

    sent = _send_email(
        subject=subject,
        template_name='emails/abandoned_cart.html',
        context={
            'abandoned_cart': abandoned_cart,
            'cart_items': cart_items or [],
        },
        to_email=email,
    )

    if sent:
        from django.utils import timezone
        abandoned_cart.reminder_sent = True
        abandoned_cart.reminder_sent_at = timezone.now()
        abandoned_cart.save(update_fields=['reminder_sent', 'reminder_sent_at'])

    return sent
