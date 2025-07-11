from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Category, Product, Order, OrderItem
from .cart import Cart
from .forms import OrderCreateForm
import requests
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from random import sample
from .recommender import get_recommendations
from django.views.decorators.csrf import csrf_exempt
import qrcode
import base64
from io import BytesIO
from decimal import Decimal

def homepage(request):  # Pastikan namanya 'homepage' bukan 'product_list'
    categories = Category.objects.all()[:4]
    all_products = list(Product.objects.filter(available=True))
    # Ambil 4 produk acak dari semua kategori
    featured_products = sample(all_products, 4) if len(all_products) > 4 else all_products
    # Ambil pesan login sukses dari session jika ada
    login_success = request.session.pop('login_success', False)
    return render(request, 'store/homepage.html', {
        'categories': categories,
        'featured_products': featured_products,
        'login_success': login_success,
    })

def catalog(request):
    category_slug = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    categories = Category.objects.all()
    
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        category = None
    if query:
        products = products.filter(name__icontains=query)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/catalog.html', {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'query': query,
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    # Rekomendasi produk mirip (content-based)
    recommended_products = get_recommendations(product, top_n=4)
    variation_types = product.variation_types.prefetch_related('values').all()
    return render(request, 'store/product.html', {
        'product': product,
        'related_products': recommended_products,
        'variation_types': variation_types,
    })

def product_detail_by_slug(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]
    variation_types = product.variation_types.prefetch_related('values').all()
    return render(request, 'store/product.html', {
        'product': product,
        'related_products': related_products,
        'variation_types': variation_types,
    })

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    size = request.POST.get('size') or request.GET.get('size') or 'L'
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    # Jika update dari cart (ada 'quantity' dan 'size' di POST), override_quantity=True
    if request.method == 'POST' and 'quantity' in request.POST and request.POST.get('size'):
        override = True
    else:
        override = False
    cart.add(product=product, quantity=quantity, size=size, override_quantity=override)
    return redirect('store:cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    size = request.GET.get('size') or request.POST.get('size') or 'L'
    cart.remove(product, size=size)
    return redirect('store:cart_detail')

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect('store:cart_detail')

def checkout(request):
    product_id = request.GET.get('product_id')
    qty = request.GET.get('qty', 1)
    size = request.GET.get('size') or None
    single_product = None

    if product_id:
        product = get_object_or_404(Product, id=product_id)
        try:
            qty = int(qty)
        except ValueError:
            qty = 1
        price = product.discount_price if product.discount_price else product.price
        total_price = price * qty
        single_product = {
            'product': product,
            'quantity': qty,
            'size': size,
            'price': price,
            'total_price': total_price,
        }
        cart_items = []
        cart_total = total_price
    else:
        cart = Cart(request)
        cart_items = list(cart)
        cart_total = cart.get_total_price()
        single_product = None

    shipping_cost = 0
    tax = 0
    total = (single_product['total_price'] if single_product else cart_total) + shipping_cost + tax

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            # Isi first_name dan last_name dari full_name jika ada
            full_name = getattr(order, 'full_name', None) or request.POST.get('full_name', '')
            if full_name:
                parts = full_name.strip().split(' ', 1)
                order.first_name = parts[0]
                order.last_name = parts[1] if len(parts) > 1 else ''
            if request.user.is_authenticated:
                order.user = request.user
            if hasattr(order, 'shipping_cost'):
                order.shipping_cost = form.cleaned_data.get('shipping_cost', 0)
            payment_method = request.POST.get('payment', 'qris')
            if hasattr(order, 'payment_method'):
                order.payment_method = payment_method
            order.save()
            form.save_m2m()
            # Simpan item order
            if single_product:
                OrderItem.objects.create(
                    order=order,
                    product=single_product['product'],
                    price=Decimal(single_product['price']),
                    quantity=single_product['quantity'],
                    size=single_product['size']
                )
            else:
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity'],
                        size=item.get('size')
                    )
                cart.clear()
            # Simpan metode pembayaran ke order
            payment_method = request.POST.get('payment', 'qris')
            if hasattr(order, 'payment_method'):
                order.payment_method = payment_method
                order.save(update_fields=['payment_method'])
            # Refresh order instance agar relasi items terupdate
            order.refresh_from_db()
            # Generate QR code jika QRIS
            qr_img = None
            if payment_method == 'qris':
                qr_data = f'ORDER-{order.id}-{order.full_name}-{order.total_cost if hasattr(order, "total_cost") else ""}'
                qr = qrcode.make(qr_data)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
                qr_img = img_str
                return render(request, 'store/konfirmasi_qris.html', {
                    'order': order,
                    'total_bayar': order.get_total_cost() + (order.shipping_cost or 0),
                    'qr_img': qr_img,
                })
            elif payment_method == 'ewallet':
                return render(request, 'store/konfirmasi_ewallet.html', {
                    'order': order,
                    'total_bayar': order.get_total_cost() + (order.shipping_cost or 0),
                })
            elif payment_method == 'bank_transfer':
                return render(request, 'store/konfirmasi_bank.html', {
                    'order': order,
                    'total_bayar': order.get_total_cost() + (order.shipping_cost or 0),
                })
            elif payment_method == 'cod':
                return render(request, 'store/konfirmasi_cod.html', {
                    'order': order,
                    'total_bayar': order.get_total_cost() + (order.shipping_cost or 0),
                })
            else:
                return render(request, 'store/konfirmasi_qris.html', {
                    'order': order,
                    'total_bayar': order.get_total_cost() + (order.shipping_cost or 0),
                })
    else:
        form = OrderCreateForm()

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total if not single_product else None,
        'single_product': single_product,
        'shipping_cost': shipping_cost,
        'tax': tax,
        'total': total,
        'form': form,
    })

def promo_page(request):
    # Get products with discount
    products = Product.objects.filter(discount_price__isnull=False).order_by('-discount_price')
    return render(request, 'store/promo.html', {
        'products': products
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Set flag login sukses di session
            request.session['login_success'] = True
            return redirect('store:homepage')
        else:
            from django.contrib import messages
            messages.error(request, 'Username atau password salah.')
    return render(request, 'store/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        # Validasi sederhana
        if not username or not email or not password1 or not password2:
            messages.error(request, 'Semua field harus diisi.')
        elif password1 != password2:
            messages.error(request, 'Password tidak cocok.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah digunakan.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            messages.success(request, 'Registrasi berhasil. Silakan login.')
            return redirect('store:login')
    return render(request, 'store/register.html')

def ajax_ongkir(request):
    if request.method == 'POST':
        api_key = '94cefef8cd74ecf05c7ecfec8bd4d9059928ec754b203b122b80f45e605ee0ad'  # API key Binderbyte
        courier = request.POST.get('courier', 'jne')
        origin = request.POST.get('origin')  # id kota/kabupaten asal
        destination = request.POST.get('destination')  # id kecamatan tujuan
        weight = request.POST.get('weight', 1000)  # berat dalam gram
        # Binderbyte endpoint
        url = f'https://api.binderbyte.com/ongkir/cost?api_key={api_key}'
        data = {
            'courier': courier,
            'origin': origin,
            'destination': destination,
            'weight': weight
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Gagal mengambil ongkir', 'detail': response.text}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

# --- AJAX Wilayah: BINDERBYTE ---
@csrf_exempt
def ajax_province(request):
    api_key = '94cefef8cd74ecf05c7ecfec8bd4d9059928ec754b203b122b80f45e605ee0ad'  # Ganti dengan API key Binderbyte Anda
    url = f'https://api.binderbyte.com/wilayah/provinsi?api_key={api_key}'
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        # Binderbyte: data['value'] = list provinsi
        results = []
        for prov in data.get('value', []):
            results.append({
                'province_id': prov.get('id'),
                'province': prov.get('name'),
            })
        return JsonResponse({'results': results})
    return JsonResponse({'results': [], 'error': f'Status: {r.status_code}', 'detail': r.text})

@csrf_exempt
def ajax_city(request):
    api_key = '94cefef8cd74ecf05c7ecfec8bd4d9059928ec754b203b122b80f45e605ee0ad'  # Ganti dengan API key Binderbyte Anda
    province_id = request.GET.get('province')
    url = f'https://api.binderbyte.com/wilayah/kabupaten?api_key={api_key}&id_provinsi={province_id}'
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        results = []
        for city in data.get('value', []):
            results.append({
                'city_id': city.get('id'),
                'city_name': city.get('name'),
            })
        return JsonResponse({'results': results})
    return JsonResponse({'results': [], 'error': f'Status: {r.status_code}', 'detail': r.text})

@csrf_exempt
def ajax_subdistrict(request):
    api_key = '94cefef8cd74ecf05c7ecfec8bd4d9059928ec754b203b122b80f45e605ee0ad'  # Ganti dengan API key Binderbyte Anda
    city_id = request.GET.get('city')
    url = f'https://api.binderbyte.com/wilayah/kecamatan?api_key={api_key}&id_kabupaten={city_id}'
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        results = []
        for subd in data.get('value', []):
            results.append({
                'subdistrict_id': subd.get('id'),
                'subdistrict_name': subd.get('name'),
            })
        return JsonResponse({'results': results})
    return JsonResponse({'results': [], 'error': f'Status: {r.status_code}', 'detail': r.text})

@login_required
def profile_view(request):
    return render(request, 'store/profile.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # Di sini bisa tambahkan logika kirim email atau simpan pesan ke database
        from django.contrib import messages
        messages.success(request, 'Pesan Anda telah dikirim. Terima kasih!')
    return render(request, 'store/contact.html')

@login_required
def order_detail_json(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = []
    for item in order.items.all():
        items.append({
            'product': str(item.product),
            'variation': str(item.variation) if hasattr(item, 'variation') and item.variation else '',
            'quantity': item.quantity,
            'price': item.price,
        })
    data = {
        'id': order.id,
        'created': order.created.strftime('%d %b %Y %H:%M'),
        'address': getattr(order, 'address', '-') or '-',
        'shipping_cost': getattr(order, 'shipping_cost', 0) or 0,
        'total_cost': order.get_total_cost(),
        'paid': order.paid,
        'items': items,
        'payment_method': getattr(order, 'payment_method', None),
        'buyer_name': f"{getattr(order, 'first_name', '-') or ''} {getattr(order, 'last_name', '-') or ''}",
    }
    return JsonResponse(data)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created').prefetch_related('items__product')
    return render(request, 'store/order_history.html', {'orders': orders})