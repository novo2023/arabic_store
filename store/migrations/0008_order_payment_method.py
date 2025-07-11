from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0007_alter_product_discount_price_alter_product_price_and_more'),
    ]
    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(max_length=30, blank=True, null=True),
        ),
    ]
