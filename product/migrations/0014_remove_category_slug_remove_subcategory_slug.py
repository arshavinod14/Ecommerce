# Generated by Django 4.1.3 on 2023-04-07 20:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0013_guestcart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='slug',
        ),
        migrations.RemoveField(
            model_name='subcategory',
            name='slug',
        ),
    ]
