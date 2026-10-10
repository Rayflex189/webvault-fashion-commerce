from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

from core.models import StoreSettings


def _send_email(subject, template_name, context, to_email):
    """Helper to send HTML emails with plain-text fallback."""
    store = StoreSettings.load()

    # Make sure store details are always available in templates
    context.update({
        'store': store,
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
    msg.send(fail_silently=True)  # Never crash the request if email fails


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
