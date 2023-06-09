# Generated by Django 4.1.3 on 2023-01-12 07:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartitems",
            name="size",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cartitems",
                to="product.size",
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="size",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product",
                to="product.size",
            ),
        ),
    ]
