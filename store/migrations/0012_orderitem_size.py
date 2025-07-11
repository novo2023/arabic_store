from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0011_order_shipping_cost'),
    ]
    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='size',
            field=models.CharField(max_length=20, blank=True, null=True),
        ),
    ]
