# Generated by Django 4.1.3 on 2023-01-16 19:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0004_product_sizes"),
    ]

    operations = [
        migrations.RemoveField(model_name="cartitems", name="size",),
    ]
