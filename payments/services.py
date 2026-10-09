import requests
from core.models import StoreSettings


def initialize_paystack_transaction(order, callback_url):
    """
    Initialize a Paystack transaction using the store owner's own secret key.
    Returns a dict with 'status' (bool) and either 'data' or 'message'.
    """
    store = StoreSettings.load()
    secret_key = store.paystack_secret_key

    if not secret_key:
        return {
            'status': False,
            'message': 'Paystack is not configured. Add your keys in Store Settings.',
        }

    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": order.email,
        "amount": int(order.total * 100),  # Paystack uses kobo (smallest unit)
        "callback_url": callback_url,
        "metadata": {
            "order_id": order.id,
            "order_number": order.order_number,
            "customer_name": order.full_name,
            "custom_fields": [
                {
                    "display_name": "Order Number",
                    "variable_name": "order_number",
                    "value": order.order_number,
                },
            ],
        },
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'status': False,
            'message': f'Could not reach payment provider: {str(e)}',
        }


def verify_paystack_transaction(reference):
    """
    Verify a Paystack transaction server-side.
    Never trust the frontend response — always call Paystack directly.
    """
    store = StoreSettings.load()
    secret_key = store.paystack_secret_key

    if not secret_key:
        return {
            'status': False,
            'message': 'Paystack is not configured.',
        }

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {secret_key}"}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            'status': False,
            'message': f'Could not verify payment: {str(e)}',
        }
