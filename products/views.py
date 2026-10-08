from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request):
    products = Product.objects.filter(is_active=True).prefetch_related('images', 'variants')
    
    # Optional filtering by category
    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)
        
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
    }
    return render(request, 'products/list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'products/detail.html', {'product': product})
