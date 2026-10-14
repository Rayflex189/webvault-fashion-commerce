from django.core.management.base import BaseCommand
from campaigns.processor import process_all_campaigns


class Command(BaseCommand):
    help = "Run all active email campaigns (cart recovery, lapsed customers, etc.)"

    def add_arguments(self, parser):
        parser.add_argument('--quiet', action='store_true', help='Suppress output')

    def handle(self, *args, **options):
        verbose = not options['quiet']
        if verbose:
            self.stdout.write("Running email campaigns...\n")

        results = process_all_campaigns(verbose=verbose)

        if verbose:
            total = sum(sent for _, sent in results)
            self.stdout.write(self.style.SUCCESS(f"\nDone. {total} email(s) sent total."))
