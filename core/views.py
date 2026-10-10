from django.shortcuts import render
from products.models import Product, Category


def home(request):
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).prefetch_related('images')[:8]

    # Fallback: if no featured products, show the 8 newest
    if not featured_products:
        featured_products = Product.objects.filter(
            is_active=True
        ).prefetch_related('images').order_by('-created_at')[:8]

    categories = Category.objects.all()[:6]

    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'home.html', context)
