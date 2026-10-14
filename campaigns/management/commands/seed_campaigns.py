from django.core.management.base import BaseCommand
from campaigns.models import EmailTemplate, EmailCampaign


CART_RECOVERY_HTML = """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
    <div style="background: #0f172a; padding: 24px; text-align: center; border-radius: 12px 12px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 22px;">You left something behind...</h1>
    </div>
    <div style="background: white; padding: 32px; border-radius: 0 0 12px 12px;">
        <p style="color: #4b5563; line-height: 1.6;">
            Hi {{ customer_name }},
        </p>
        <p style="color: #4b5563; line-height: 1.6;">
            Your cart at <strong>{{ store_name }}</strong> is still waiting for you.
            You have <strong>{{ item_count }} item(s)</strong> worth
            <strong>₦{{ subtotal }}</strong>.
        </p>

        <table style="width: 100%; border-collapse: collapse; margin: 24px 0;">
            {{ cart_items }}
        </table>

        <div style="text-align: center; margin: 32px 0;">
            <a href="{{ recovery_url }}"
               style="background: #4F46E5; color: white; padding: 14px 32px; border-radius: 8px;
                      text-decoration: none; font-weight: bold; display: inline-block;">
                Complete My Order
            </a>
        </div>

        <p style="color: #9ca3af; font-size: 12px; text-align: center; margin-top: 32px;">
            &copy; {{ store_name }}
        </p>
    </div>
</div>
"""


LAPSED_CUSTOMER_HTML = """
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">
    <div style="background: #0f172a; padding: 24px; text-align: center; border-radius: 12px 12px 0 0;">
        <h1 style="color: white; margin: 0; font-size: 22px;">We miss you!</h1>
    </div>
    <div style="background: white; padding: 32px; border-radius: 0 0 12px 12px;">
        <p style="color: #4b5563; line-height: 1.6;">
            Hi {{ customer_name }},
        </p>
        <p style="color: #4b5563; line-height: 1.6;">
            We haven't seen you in a while! New styles have just arrived at
            <strong>{{ store_name }}</strong>. Come see what's new.
        </p>

        <div style="text-align: center; margin: 32px 0;">
            <a href="{{ site_url }}/shop/"
               style="background: #4F46E5; color: white; padding: 14px 32px; border-radius: 8px;
                      text-decoration: none; font-weight: bold; display: inline-block;">
                Shop New Arrivals
            </a>
        </div>
    </div>
</div>
"""


class Command(BaseCommand):
    help = "Seeds default email templates and campaigns."

    def handle(self, *args, **options):
        # Cart recovery
        t1, _ = EmailTemplate.objects.get_or_create(
            name="Cart Recovery — 4hr",
            defaults={
                'subject': "You left something behind at {{ store_name }}",
                'body_html': CART_RECOVERY_HTML,
            }
        )

        c1, created1 = EmailCampaign.objects.get_or_create(
            name="Cart Recovery — 4hr",
            trigger='cart_abandoned',
            delay_hours=4,
            defaults={'template': t1, 'is_active': True}
        )
        if created1:
            self.stdout.write(self.style.SUCCESS(f"✓ Created campaign: {c1.name}"))

        # Lapsed customer
        t2, _ = EmailTemplate.objects.get_or_create(
            name="Lapsed Customer — 30 day",
            defaults={
                'subject': "We miss you at {{ store_name }}!",
                'body_html': LAPSED_CUSTOMER_HTML,
            }
        )

        c2, created2 = EmailCampaign.objects.get_or_create(
            name="Lapsed Customer — 30 day",
            trigger='customer_lapsed',
            delay_hours=720,  # 30 days
            defaults={'template': t2, 'is_active': False}  # Off by default
        )
        if created2:
            self.stdout.write(self.style.SUCCESS(f"✓ Created campaign: {c2.name}"))

        self.stdout.write(self.style.SUCCESS("\nDone! Visit /admin/ to customize your campaigns."))
