from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from products.models import ProductVariant
from delivery.models import DeliveryMethod
from core.models import StoreSettings
from .cart import Cart
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.db.models import Q


@login_required
def my_orders(request):
    """Logged-in user's order history."""
    orders = Order.objects.filter(
        Q(user=request.user) | Q(email=request.user.email)
    ).order_by('-created_at')

    return render(request, 'orders/my_orders.html', {'orders': orders})


def order_detail(request, order_number):
    """View a single order. Only buyer (logged in) or via tracking can see details."""
    order = get_object_or_404(Order, order_number=order_number)

    # Security: only allow access if user owns the order OR email matches
    is_owner = (
        request.user.is_authenticated and
        (order.user == request.user or order.email == request.user.email)
    )

    if not is_owner:
        # If not logged in, we allow view-only via tracking link
        # but we don't show sensitive info (only status timeline)
        return render(request, 'orders/order_public.html', {'order': order})

    return render(request, 'orders/order_detail.html', {'order': order})


def track_order(request):
    """Public order tracking page — customer enters order number + email."""
    order = None
    error = ''

    if request.method == 'POST':
        order_number = request.POST.get('order_number', '').strip()
        email = request.POST.get('email', '').strip().lower()

        try:
            order = Order.objects.get(order_number=order_number, email=email)
        except Order.DoesNotExist:
            error = 'No order found with that number and email combination.'

    return render(request, 'orders/track.html', {'order': order, 'error': error})


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'orders/cart.html', {'cart': cart})


def cart_add(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if variant.stock <= 0:
        messages.error(request, 'This item is out of stock.')
        return redirect(request.META.get('HTTP_REFERER', 'products:list'))

    quantity = int(request.POST.get('quantity', 1))
    cart.add(variant.id, quantity)
    messages.success(request, f'Added {variant.product.name} to cart.')
    return redirect('orders:cart')


def cart_update(request, variant_id):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.update(variant_id, quantity)
    return redirect('orders:cart')


def cart_remove(request, variant_id):
    cart = Cart(request)
    cart.remove(variant_id)
    messages.success(request, 'Item removed from cart.')
    return redirect('orders:cart')


def checkout(request):
    cart = Cart(request)

    if cart.is_empty():
        messages.error(request, 'Your cart is empty.')
        return redirect('products:list')

    delivery_methods = DeliveryMethod.objects.filter(is_active=True)
    store = StoreSettings.load()

    if request.method == 'POST':
        delivery_method_id = request.POST.get('delivery_method')
        delivery_method = get_object_or_404(DeliveryMethod, id=delivery_method_id, is_active=True)

        with transaction.atomic():
            subtotal = cart.get_subtotal()
            delivery_fee = delivery_method.fee
            total = subtotal + delivery_fee

            order = Order.objects.create(
                full_name=request.POST.get('full_name', ''),
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', ''),
                city=request.POST.get('city', ''),
                state=request.POST.get('state', ''),
                delivery_method=delivery_method,
                delivery_fee=delivery_fee,
                subtotal=subtotal,
                total=total,
                currency=store.currency,
                notes=request.POST.get('notes', ''),
                user=request.user if request.user.is_authenticated else None,
            )

            for item in cart:
                variant = item['variant']
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    product_name=variant.product.name,
                    size_name=variant.size.name,
                    color_name=variant.color.name,
                    price=item['price'],
                    quantity=item['quantity'],
                )

            # NOTE: Paystack goes here (Option D). For now, we go to the confirmation page.
            cart.clear()
            return redirect('orders:order_confirmation', order_number=order.order_number)

    context = {
        'cart': cart,
        'delivery_methods': delivery_methods,
        'store': store,
    }
    return render(request, 'orders/checkout.html', context)


def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/confirmation.html', {'order': order})
