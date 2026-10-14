from datetime import timedelta
from django.utils import timezone
from django.template import Template, Context
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from core.models import StoreSettings
from orders.models import AbandonedCart, Order
from django.contrib.auth.models import User

from .models import EmailCampaign, CampaignLog


# ─────────────────────────────────────────
# TEMPLATE RENDERING
# ─────────────────────────────────────────

def _render(template_string, context):
    """Render a template string with Django's engine."""
    return Template(template_string).render(Context(context))


def _build_cart_items_html(items):
    """Turn items_snapshot JSON into clean HTML rows for emails."""
    rows = []
    for item in items:
        rows.append(f"""
        <tr>
            <td style="padding:8px 0;color:#374151;">
                {item['product_name']} ({item['size']}/{item['color']}) × {item['quantity']}
            </td>
            <td style="padding:8px 0;text-align:right;color:#111827;font-weight:bold;">
                ₦{item['price'] * item['quantity']:,.2f}
            </td>
        </tr>
        """)
    return "".join(rows)


# ─────────────────────────────────────────
# THE MAIN DISPATCHER
# ─────────────────────────────────────────

def _send_campaign_email(campaign, recipient_email, context):
    """Send a single campaign email and log it."""
    store = StoreSettings.load()

    subject = _render(campaign.template.subject, context)
    body_html = _render(campaign.template.body_html, context)

    from_email = f"{store.store_name} <{settings.DEFAULT_FROM_EMAIL}>"

    msg = EmailMultiAlternatives(
        subject=subject,
        body=_render(campaign.template.body_text, context) if campaign.template.body_text else "",
        from_email=from_email,
        to=[recipient_email],
    )
    msg.attach_alternative(body_html, "text/html")

    try:
        msg.send(fail_silently=False)
        CampaignLog.objects.create(
            campaign=campaign,
            recipient_email=recipient_email,
            subject=subject,
            status='sent',
        )
        campaign.sent_count += 1
        campaign.last_run_at = timezone.now()
        campaign.save(update_fields=['sent_count', 'last_run_at'])
        return True
    except Exception as e:
        CampaignLog.objects.create(
            campaign=campaign,
            recipient_email=recipient_email,
            subject=subject,
            status='failed',
            error_message=str(e),
        )
        return False


# ─────────────────────────────────────────
# TRIGGER HANDLERS
# ─────────────────────────────────────────

def _process_cart_abandoned(campaign):
    """Find carts older than the campaign delay and send them reminders."""
    store = StoreSettings.load()
    threshold = timezone.now() - timedelta(hours=campaign.delay_hours)

    carts = AbandonedCart.objects.filter(
        is_converted=False,
        reminder_sent=False,
        item_count__gt=0,
        updated_at__lt=threshold,
    ).exclude(email='')

    sent = 0
    for cart in carts:
        email = cart.email or (cart.user.email if cart.user else '')
        if not email:
            continue

        # Build recovery URL
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
        recovery_url = f"{site_url}/cart/restore/{cart.recovery_token}/"

        customer_name = ""
        if cart.user:
            customer_name = cart.user.first_name or cart.user.email.split('@')[0]

        context = {
            'store': store,
            'store_name': store.store_name,
            'customer_name': customer_name,
            'item_count': cart.item_count,
            'subtotal': cart.subtotal,
            'cart_items': _build_cart_items_html(cart.items_snapshot),
            'recovery_url': recovery_url,
            'site_url': site_url,
        }

        if _send_campaign_email(campaign, email, context):
            cart.reminder_sent = True
            cart.reminder_sent_at = timezone.now()
            cart.save(update_fields=['reminder_sent', 'reminder_sent_at'])
            sent += 1

    return sent


def _process_customer_lapsed(campaign):
    """Email customers who haven't ordered in 30+ days."""
    store = StoreSettings.load()
    threshold = timezone.now() - timedelta(days=30)
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')

    # Find users whose most recent order is older than 30 days
    lapsed_users = User.objects.filter(
        is_staff=False,
        is_active=True,
        orders__created_at__lt=threshold,
    ).distinct()

    sent = 0
    for user in lapsed_users:
        # Skip if already sent to this user in this campaign
        if CampaignLog.objects.filter(
            campaign=campaign,
            recipient_email=user.email,
        ).exists():
            continue

        context = {
            'store': store,
            'store_name': store.store_name,
            'customer_name': user.first_name or user.email.split('@')[0],
            'site_url': site_url,
        }

        if _send_campaign_email(campaign, user.email, context):
            sent += 1

    return sent


# ─────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────

TRIGGER_HANDLERS = {
    'cart_abandoned': _process_cart_abandoned,
    'customer_lapsed': _process_customer_lapsed,
}


def process_all_campaigns(verbose=False):
    """
    Iterate over all active campaigns and run their handlers.
    Called by Celery or by the management command.
    """
    results = []
    campaigns = EmailCampaign.objects.filter(is_active=True).select_related('template')

    for campaign in campaigns:
        handler = TRIGGER_HANDLERS.get(campaign.trigger)

        if handler is None:
            if verbose:
                print(f"⚠️  No handler for trigger '{campaign.trigger}' — skipping '{campaign.name}'")
            continue

        try:
            sent = handler(campaign)
            results.append((campaign.name, sent))
            if verbose:
                print(f"✓ {campaign.name}: {sent} email(s) sent")
        except Exception as e:
            if verbose:
                print(f"✗ {campaign.name} failed: {e}")

    return results
