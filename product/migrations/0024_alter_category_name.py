# Generated by Django 4.1.3 on 2023-04-18 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0023_cartitems_discount"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=250, unique=True),
        ),
    ]
