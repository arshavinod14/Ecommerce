# Generated by Django 4.1.3 on 2023-03-28 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0011_remove_category_slug_remove_subcategory_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="slug",
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="subcategory",
            name="slug",
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]