# Generated by Django 5.2 on 2025-05-06 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_cartitem_product_wishlistitem_delete_shirt_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sizes',
            field=models.CharField(default='S', help_text='Comma-separated sizes, e.g. S,M,L,XL', max_length=100),
        ),
    ]
