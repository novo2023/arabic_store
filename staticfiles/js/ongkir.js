$(document).ready(function() {
    // Ganti selector sesuai id/kode kota asal toko Anda
    const originCityId = 501; // contoh: Jakarta Pusat
    let weight = 1000; // default berat, bisa diubah sesuai total belanja

    // Trigger saat kecamatan dipilih
    $('#city').on('change', function() {
        const destination = $(this).val();
        const courier = $('#shipping').val() || 'jne';
        if (!destination) return;
        $.ajax({
            url: '/ajax/ongkir/',
            method: 'POST',
            data: {
                origin: originCityId,
                destination: destination,
                weight: weight,
                courier: courier,
                csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(res) {
                if (res.rajaongkir && res.rajaongkir.results && res.rajaongkir.results.length > 0) {
                    const costs = res.rajaongkir.results[0].costs;
                    if (costs.length > 0) {
                        // Pilih layanan termurah
                        let minCost = costs[0].cost[0].value;
                        let service = costs[0].service;
                        costs.forEach(function(item) {
                            if (item.cost[0].value < minCost) {
                                minCost = item.cost[0].value;
                                service = item.service;
                            }
                        });
                        $('#ongkir-value').text('Rp ' + minCost.toLocaleString() + ' (' + service + ')');
                        // Update total pembayaran
                        let subtotal = 0;
                        if ($('#subtotal-value').length) {
                            subtotal = parseInt($('#subtotal-value').data('subtotal'));
                        } else if ($('#cart_total').length) {
                            subtotal = parseInt($('#cart_total').text().replace(/\D/g, ''));
                        }
                        $('#total-value').text('Rp ' + (subtotal + minCost).toLocaleString());
                        // Set shipping_cost ke form
                        if (typeof setShippingCost === 'function') setShippingCost(minCost);
                    }
                } else {
                    $('#ongkir-value').text('Tidak ada data ongkir');
                    if (typeof setShippingCost === 'function') setShippingCost(0);
                }
            },
            error: function() {
                // Jika gagal ambil ongkir, set ongkir manual Rp14.000
                var ongkirManual = 14000;
                $('#ongkir-value').text('Rp ' + ongkirManual.toLocaleString() + '');
                // Update total pembayaran
                let subtotal = 0;
                if ($('#subtotal-value').length) {
                    subtotal = parseInt($('#subtotal-value').data('subtotal'));
                } else if ($('#cart_total').length) {
                    subtotal = parseInt($('#cart_total').text().replace(/\D/g, ''));
                } else if ($('#total-value').length) {
                    // fallback jika subtotal tidak ada, ambil dari data-total
                    subtotal = parseInt($('#total-value').attr('data-total')) || 0;
                }
                $('#total-value').text('Rp ' + (subtotal + ongkirManual).toLocaleString());
                // Set shipping_cost manual ke form
                if (typeof setShippingCost === 'function') setShippingCost(ongkirManual);
            }
        });
    });
    // Trigger ulang jika user ganti kurir
    $('#shipping').on('change', function() {
        $('#city').trigger('change');
    });
});

function setShippingCost(cost) {
    // Pastikan input hidden shipping_cost ada
    $("#shipping_cost").val(cost);
}
