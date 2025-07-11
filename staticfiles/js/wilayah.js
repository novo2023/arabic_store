$(document).ready(function() {
    // Set default options
    $('#province').html('<option value="">Pilih Provinsi</option>');
    $('#city').html('<option value="">Pilih Kota/Kabupaten</option>');
    $('#subdistrict').html('<option value="">Pilih Kecamatan</option>');

    // Disable city & subdistrict until province selected
    $('#city').prop('disabled', true);
    $('#subdistrict').prop('disabled', true);

    // 1. Load provinsi
    $.ajax({
        url: '/ajax/province/',
        method: 'GET',
        success: function(res) {
            if(res.results && res.results.length > 0) {
                res.results.forEach(function(prov) {
                    $('#province').append('<option value="'+prov.province_id+'">'+prov.province+'</option>');
                });
                $('#province').prop('disabled', false);
            } else {
                $('#province').html('<option value="">Tidak ada data provinsi</option>');
            }
        },
        error: function() {
            $('#province').html('<option value="">Gagal load provinsi</option>');
        }
    });

    // 2. Load kota/kabupaten saat provinsi dipilih
    $('#province').on('change', function() {
        var provinceId = $(this).val();
        $('#city').html('<option value="">Pilih Kota/Kabupaten</option>');
        $('#subdistrict').html('<option value="">Pilih Kecamatan</option>');
        $('#city').prop('disabled', true);
        $('#subdistrict').prop('disabled', true);
        if(!provinceId) return;
        $.ajax({
            url: '/ajax/city/?province='+provinceId,
            method: 'GET',
            success: function(res) {
                if(res.results && res.results.length > 0) {
                    res.results.forEach(function(city) {
                        $('#city').append('<option value="'+city.city_id+'">'+city.city_name+'</option>');
                    });
                    $('#city').prop('disabled', false);
                } else {
                    $('#city').html('<option value="">Tidak ada data kota</option>');
                }
            },
            error: function() {
                $('#city').html('<option value="">Gagal load kota</option>');
            }
        });
    });

    // 3. Load kecamatan saat kota dipilih
    $('#city').on('change', function() {
        var cityId = $(this).val();
        $('#subdistrict').html('<option value="">Pilih Kecamatan</option>');
        $('#subdistrict').prop('disabled', true);
        if(!cityId) return;
        $.ajax({
            url: '/ajax/subdistrict/?city='+cityId,
            method: 'GET',
            success: function(res) {
                if(res.results && res.results.length > 0) {
                    res.results.forEach(function(subd) {
                        $('#subdistrict').append('<option value="'+subd.subdistrict_id+'">'+subd.subdistrict_name+'</option>');
                    });
                    $('#subdistrict').prop('disabled', false);
                } else {
                    $('#subdistrict').html('<option value="">Tidak ada data kecamatan</option>');
                }
            },
            error: function() {
                $('#subdistrict').html('<option value="">Gagal load kecamatan</option>');
            }
        });
    });
});
