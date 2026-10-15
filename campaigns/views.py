from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import os

from .processor import process_all_campaigns


@csrf_exempt
@require_POST
def run_campaigns_webhook(request):
    """
    Securely trigger all active campaigns.

    Called on a schedule by GitHub Actions (or any external cron service).
    Protected by a shared secret stored in the CRON_SECRET env var.

    URL: POST /campaigns/run-webhook/?secret=<CRON_SECRET>
    """
    secret = request.GET.get('secret', '')
    expected = os.environ.get('CRON_SECRET', '')

    # Reject if secret is missing or wrong
    if not expected or secret != expected:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    results = process_all_campaigns(verbose=False)
    total_sent = sum(sent for _, sent in results)

    return JsonResponse({
        'status': 'ok',
        'campaigns_run': len(results),
        'emails_sent': total_sent,
        'details': [{'name': name, 'sent': sent} for name, sent in results],
    })
