# store/urls.py
from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'store'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('produk/<slug:slug>/', views.product_detail_by_slug, name='product_detail_by_slug'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout, name='checkout'),
    path('promo/', views.promo_page, name='promo'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('ajax/ongkir/', views.ajax_ongkir, name='ajax_ongkir'),
    path('ajax/province/', views.ajax_province, name='ajax_province'),
    path('ajax/city/', views.ajax_city, name='ajax_city'),
    path('ajax/subdistrict/', views.ajax_subdistrict, name='ajax_subdistrict'),
    path('profile/', views.profile_view, name='profile'),
    path('contact/', views.contact, name='contact'),
    path('orders/history/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/json/', views.order_detail_json, name='order_detail_json'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]