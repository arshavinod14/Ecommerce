# Generated by Django 4.1.3 on 2023-03-19 20:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_address'),
        ('order', '0002_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='shipping_address', to='store.address'),
        ),
    ]
