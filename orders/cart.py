from products.models import ProductVariant


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, variant_id, quantity=1):
        variant_id = str(variant_id)
        self.cart[variant_id] = self.cart.get(variant_id, 0) + quantity
        self.save()

    def update(self, variant_id, quantity):
        variant_id = str(variant_id)
        if quantity > 0:
            self.cart[variant_id] = quantity
        else:
            self.remove(variant_id)
        self.save()

    def remove(self, variant_id):
        variant_id = str(variant_id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def __iter__(self):
        variant_ids = list(self.cart.keys())
        variants = ProductVariant.objects.filter(id__in=variant_ids).select_related(
            'product', 'size', 'color'
        )
        for variant in variants:
            quantity = self.cart[str(variant.id)]
            yield {
                'variant': variant,
                'quantity': quantity,
                'price': variant.final_price,
                'line_total': variant.final_price * quantity,
            }

    def __len__(self):
        return sum(self.cart.values())

    def get_subtotal(self):
        return sum(item['line_total'] for item in self)

    def is_empty(self):
        return len(self.cart) == 0
