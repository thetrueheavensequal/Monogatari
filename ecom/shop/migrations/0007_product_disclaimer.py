# Generated by Django 5.2 on 2025-05-07 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_product_care_product_composition'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='disclaimer',
            field=models.TextField(blank=True),
        ),
    ]
