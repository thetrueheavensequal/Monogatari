# Generated by Django 5.2 on 2025-05-13 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_order_orderitem_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='gender',
            field=models.CharField(choices=[('men', 'Men'), ('women', 'Women')], default='unisex', max_length=10),
        ),
    ]
