from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from orders.models import Order
from core.models import StoreSettings
from .gateways import get_active_gateway


def initiate_payment(request, order_number):
    """
    Called when the customer clicks 'Pay Now'.
    Initializes a transaction with the store's active payment gateway
    and redirects to the gateway's secure checkout page.
    """
    order = get_object_or_404(Order, order_number=order_number)
    store = StoreSettings.load()

    # Block re-payment
    if order.status == 'paid':
        messages.info(request, 'This order has already been paid.')
        return redirect('orders:order_confirmation', order_number=order.order_number)

    if order.status == 'cancelled':
        messages.error(request, 'This order was cancelled and cannot be paid.')
        return redirect('orders:order_confirmation', order_number=order.order_number)

    # Check that online payment is enabled and configured
    gateway = get_active_gateway()
    if not gateway:
        messages.error(
            request,
            'Online payment is not available for this store. '
            'Please contact us to complete your order via bank transfer.'
        )
        return redirect('orders:order_confirmation', order_number=order.order_number)

    # Build the absolute callback URL for the gateway to redirect back to
    callback_url = request.build_absolute_uri(reverse('payments:callback'))

    # Initialize the transaction
    response = gateway.initialize(order, callback_url)

    if response.get('status'):
        # Redirect customer to the payment gateway's secure page
        return redirect(response['data']['authorization_url'])

    # Something went wrong during initialization
    error_message = response.get('message', 'Could not start payment. Please try again.')
    messages.error(request, error_message)
    return redirect('orders:order_confirmation', order_number=order.order_number)


def payment_callback(request):
    """
    Gateway redirects the customer here after payment.
    We verify the transaction SERVER-SIDE before marking the order as paid.
    """
    reference = request.GET.get('reference') or request.GET.get('trxref')

    if not reference:
        return render(request, 'payments/failed.html', {
            'reason': 'No payment reference was provided.'
        })

    gateway = get_active_gateway()
    if not gateway:
        return render(request, 'payments/failed.html', {
            'reason': 'Payment gateway is not configured.'
        })

    response = gateway.verify(reference)

    if not response.get('status'):
        return render(request, 'payments/failed.html', {
            'reason': response.get('message', 'Payment verification failed.')
        })

    data = response.get('data', {})

    if data.get('status') != 'success':
        return render(request, 'payments/failed.html', {
            'reason': f"Transaction status: {data.get('status', 'unknown')}"
        })

    # Payment verified — update the order
    order_number = data.get('metadata', {}).get('order_number')
    if not order_number:
        return render(request, 'payments/failed.html', {
            'reason': 'Could not match this payment to an order.'
        })

    order = get_object_or_404(Order, order_number=order_number)

    # Idempotency: only update if not already paid
    if order.status != 'paid':
        order.status = 'paid'
        order.save()

    return render(request, 'payments/success.html', {'order': order})
