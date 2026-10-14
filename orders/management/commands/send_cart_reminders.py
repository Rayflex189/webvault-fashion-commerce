from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from orders.models import AbandonedCart
from orders.emails import send_abandoned_cart_email


class Command(BaseCommand):
    help = "Send reminder emails for abandoned carts older than N hours."

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=4,
            help='Minimum cart idle time in hours (default: 4)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be sent without actually sending emails',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        dry_run = options['dry_run']
        threshold = timezone.now() - timedelta(hours=hours)

        # Find abandoned carts that need reminders
        carts = AbandonedCart.objects.filter(
            is_converted=False,
            reminder_sent=False,
            item_count__gt=0,
            updated_at__lt=threshold,
        ).exclude(email='').select_related('user')

        self.stdout.write(f"Found {carts.count()} candidate cart(s) to remind.")

        sent = 0
        skipped = 0
        for cart in carts:
            # Resolve email
            email = cart.email or (cart.user.email if cart.user else '')
            if not email:
                skipped += 1
                continue

            # Rebuild a lightweight item list for the email
            from orders.cart import Cart  # local import to avoid circulars
            # We don't have the raw session, so we can't easily read cart contents.
            # Instead we rely on the snapshot fields we stored.

            cart_items = []  # Empty fallback — see note below

            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f"[DRY RUN] Would send to: {email} "
                    f"({cart.item_count} items, {cart.subtotal} subtotal)"
                ))
                sent += 1
                continue

            send_abandoned_cart_email(cart, cart_items)
            sent += 1
            self.stdout.write(self.style.SUCCESS(f"✓ Sent to {email}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Sent: {sent}, Skipped (no email): {skipped}, Dry-run: {dry_run}"
        ))
