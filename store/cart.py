from decimal import Decimal
from django.conf import settings
from store.models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def add(self, product, quantity=1, size=None, override_quantity=False):
        key = self._make_key(product, size)
        if key not in self.cart:
            self.cart[key] = {
                'quantity': 0,
                'price': str(product.discount_price or product.price),
                'size': size or 'L',
                'product_id': product.id
            }
        
        if override_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity
        self.save()
    
    def save(self):
        self.session.modified = True
    
    def remove(self, product, size=None):
        key = self._make_key(product, size)
        # Hapus key dengan size (format baru)
        if key in self.cart:
            del self.cart[key]
            self.save()
        # Jika tidak ada, coba hapus key lama (tanpa size)
        elif str(product.id) in self.cart:
            del self.cart[str(product.id)]
            self.save()
    
    def _make_key(self, product, size):
        """Helper method to create a consistent key for the cart item."""
        if size:
            return f"{product.id}_{size}"
        return str(product.id)
    
    def __iter__(self):
        # Only use numeric keys for product lookup
        product_ids = [item['product_id'] for item in self.cart.values() if 'product_id' in item]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}
        for key, item in self.cart.items():
            if 'product_id' not in item:
                continue  # skip legacy/invalid items
            pid = str(item['product_id'])
            if pid in product_map:
                item['product'] = product_map[pid]
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item
    
    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()