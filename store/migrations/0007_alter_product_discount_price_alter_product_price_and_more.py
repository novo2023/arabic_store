# Generated by Django 5.2.3 on 2025-06-29 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_productvariationvalue_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='discount_price',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='productvariationvalue',
            name='price',
            field=models.PositiveIntegerField(blank=True, help_text='Harga khusus untuk value ini (opsional)', null=True),
        ),
    ]
