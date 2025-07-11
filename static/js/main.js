// Fungsi untuk menambahkan efek animasi pada tombol
// Hanya aktifkan animasi jika tombol add-to-cart ada di halaman detail produk dan tombolnya <button> (bukan <a>)
if (document.querySelector('.product-detail')) {
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            // Jika tombol adalah <a> (katalog), jangan animasi dan biarkan default
            if (this.tagName === 'A') {
                e.preventDefault();
                window.location = this.href;
                return false;
            }
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-check"></i> Ditambahkan';
            this.style.background = '#27ae60';
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.background = '#d4a574';
            }, 2000);
        }, false);
    });
}

// Fungsi untuk menu aktif
document.querySelectorAll('.nav-item').forEach(item => {
    if (window.location.pathname === item.getAttribute('href')) {
        item.classList.add('active');
    }
});

// Fungsi untuk kuantitas produk
function increaseQuantity() {
    const quantityInput = document.getElementById('quantity');
    quantityInput.value = parseInt(quantityInput.value) + 1;
}

function decreaseQuantity() {
    const quantityInput = document.getElementById('quantity');
    if (parseInt(quantityInput.value) > 1) {
        quantityInput.value = parseInt(quantityInput.value) - 1;
    }
}

// Fungsi untuk galeri produk
document.querySelectorAll('.thumbnail').forEach(thumb => {
    thumb.addEventListener('click', function() {
        const mainImage = document.querySelector('.main-image');
        mainImage.src = this.src;
    });
});