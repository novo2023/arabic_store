from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, Order, OrderItem
from .models_variation import ProductVariationType, ProductVariationValue
import nested_admin

# Custom admin interface: logo, judul, favicon, dan warna
from django.conf import settings

admin.site.site_header = "Arabic Store Admin"
admin.site.site_title = "Arabic Store Admin Portal"
admin.site.index_title = "Selamat Datang di Dashboard Admin Arabic Store"

class ProductVariationValueInline(nested_admin.NestedTabularInline):
    model = ProductVariationValue
    extra = 1
    fields = ('value', 'stock', 'price')

class ProductVariationTypeInline(nested_admin.NestedTabularInline):
    model = ProductVariationType
    extra = 1
    inlines = [ProductVariationValueInline]

@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = ['name', 'price', 'stock', 'available', 'display_image']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['display_image']
    inlines = [ProductVariationTypeInline]
    
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No Image"
    
    display_image.short_description = 'Preview Gambar'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'paid']
    list_filter = ['paid', 'created', 'updated']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']
    search_fields = ['order__id', 'product__name']