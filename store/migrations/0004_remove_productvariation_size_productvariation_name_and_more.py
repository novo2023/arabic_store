# Generated by Django 5.2.3 on 2025-06-29 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_product_category_alter_product_image_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariation',
            name='size',
        ),
        migrations.AddField(
            model_name='productvariation',
            name='name',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productvariation',
            name='value',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
