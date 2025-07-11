from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from .models_variation import ProductVariationType, ProductVariationValue
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name
    
    def product_count(self):
        # Menghitung jumlah produk aktif (available) di kategori ini
        return self.product.filter(available=True).count()
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.PositiveIntegerField()
    discount_price = models.PositiveIntegerField(blank=True, null=True)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    
    image = models.ImageField(upload_to='product/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("store:product_detail", args=[self.id, self.slug])
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100, default='Nama belum diisi')
    email = models.EmailField(default='aaaa@gmail.com')
    address = models.CharField(max_length=250, default='Alamat belum diisi')
    city = models.CharField(max_length=100, default='Kota Belum diisi')
    phone = models.CharField(max_length=20, default='')
    shipping_cost = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=30, blank=True, null=True)
    
    class Meta:
        ordering = ('-created',)
    
    def __str__(self):
        return f'Order {self.id}'
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=20, blank=True, null=True)  # Tambah field size/variasi
    
    def __str__(self):
        return str(self.id)
    
    def get_cost(self):
        return self.price * self.quantity