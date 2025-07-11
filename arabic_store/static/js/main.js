// Fungsi untuk menambahkan efek animasi pada tombol
document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function() {
        const originalText = this.innerHTML;
        this.innerHTML = '<i class="fas fa-check"></i> Ditambahkan';
        this.style.background = '#27ae60';
        
        setTimeout(() => {
            this.innerHTML = originalText;
            this.style.background = '#d4a574';
        }, 2000);
    });
});

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