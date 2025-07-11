import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
import nltk
from nltk.tokenize import word_tokenize
# nltk.download('punkt')  # Uncomment this line once to download tokenizer data

# Daftar FAQ/manual sederhana
FAQ_LIST = [
    (['Halo', 'Hai', 'Assalamualaikum', 'Selamat pagi', 'Selamat siang', 'Selamat sore', 'Selamat malam', 'pesan produk', 'beli', 'belanja', 'pemesanan', 'pembelian'],
     'Selamat datang, ada yang bisa kami bantu?'),
    (['cara belanja', 'bagaimana belanja', 'order', 'pesan produk', 'beli', 'belanja', 'pemesanan', 'pembelian'],
     'Untuk belanja, pilih produk lalu klik "Lihat Detail" dan ikuti proses checkout.'),
    (['ongkir', 'biaya kirim', 'pengiriman', 'ongkos kirim', 'tarif kirim', 'tarif pengiriman', 'biaya antar'],
     'Ongkir dihitung otomatis saat checkout berdasarkan alamat tujuan dan berat produk.'),
    (['metode pembayaran', 'bayar', 'qris', 'transfer', 'ewallet', 'cod', 'pembayaran', 'cara bayar', 'pembayaran qris', 'pembayaran transfer'],
     'Kami menerima pembayaran QRIS, e-wallet, transfer bank, dan COD.'),
    (['status pesanan', 'cek pesanan', 'order saya', 'lacak pesanan', 'tracking', 'pesanan saya', 'status order', 'cek order'],
     'Untuk cek status pesanan, login lalu buka menu profil.'),
    (['kontak', 'customer service', 'admin', 'hubungi', 'nomor admin', 'whatsapp', 'cs', 'bantuan'],
     'Hubungi kami melalui halaman Kontak atau WhatsApp di footer website.'),
    (['produk asli', 'keaslian', 'ori', 'original', 'asli', 'keaslian produk', 'produk ori'],
     'Semua produk di Arabic Store dijamin 100% asli dan berkualitas.'),
    (['promo', 'diskon', 'potongan harga', 'voucher', 'kode promo', 'promo terbaru', 'diskon terbaru'],
     'Promo dan diskon terbaru bisa dilihat di halaman Promo.'),
    (['alamat toko', 'lokasi toko', 'toko offline', 'buka dimana', 'alamat arabic store'],
     'Saat ini Arabic Store hanya melayani penjualan online. Info lebih lanjut hubungi admin.'),
    (['retur', 'pengembalian', 'refund', 'tukar barang', 'barang rusak', 'retur produk'],
     'Jika ada kendala retur atau pengembalian, silakan hubungi admin dengan menyertakan bukti pembelian.'),
    (['jam operasional', 'jam buka', 'waktu layanan', 'operasional toko'],
     'Layanan admin online setiap hari pukul 08.00-21.00 WIB.'),
]

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotAPIView(View):
    def post(self, request):
        import json
        try:
            data = json.loads(request.body)
            user_message = data.get('question', '').lower()
            if not user_message:
                return JsonResponse({'answer': 'Silakan ketik pertanyaan Anda.'})
            # Tokenisasi pertanyaan user
            try:
                tokens = word_tokenize(user_message)
            except Exception as e:
                return JsonResponse({'answer': f'Error tokenizing: {str(e)}'})
            # Cari jawaban di FAQ dengan token
            for keywords, answer in FAQ_LIST:
                if any(any(k.lower() in token for token in tokens) for k in keywords):
                    return JsonResponse({'answer': answer})
            # Default jika tidak ditemukan
            return JsonResponse({'answer': 'Maaf, pertanyaan Anda belum tersedia di FAQ. Silakan hubungi admin untuk info lebih lanjut.'})
        except Exception as e:
            return JsonResponse({'answer': 'Terjadi kesalahan. Silakan coba lagi.'})
