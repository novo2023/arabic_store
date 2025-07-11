from django.db import models

class ProductVariationType(models.Model):
    product = models.ForeignKey('Product', related_name='variation_types', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)  # contoh: Ukuran, Warna, Volume

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class ProductVariationValue(models.Model):
    variation_type = models.ForeignKey(ProductVariationType, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=30) # contoh: S, M, L, Merah, 100ml
    stock = models.PositiveIntegerField(default=0)
    price = models.PositiveIntegerField(blank=True, null=True, help_text="Harga khusus untuk value ini (opsional)")

    def __str__(self):
        return f"{self.variation_type} : {self.value}"
