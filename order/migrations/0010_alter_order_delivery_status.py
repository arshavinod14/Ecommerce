# Generated by Django 4.1.3 on 2023-03-29 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0009_alter_order_delivery_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="delivery_status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending"),
                    ("Confirmed", "Confirmed"),
                    ("Shipped", "Shipped"),
                    ("Out for delivery", "Out for delivery"),
                    ("Delivered", "Delivered"),
                    ("Cancelled", "Cancelled"),
                ],
                max_length=200,
            ),
        ),
    ]