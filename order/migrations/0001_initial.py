# Generated by Django 4.1.3 on 2023-03-19 05:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0005_remove_cartitems_size'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=120)),
                ('payment_method', models.CharField(max_length=120)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=6)),
                ('status', models.CharField(max_length=120)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order_id', models.CharField(default=None, max_length=200, unique=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('quantity', models.IntegerField()),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('payment_id', models.CharField(max_length=200, null=True)),
                ('payment_method', models.CharField(choices=[('1', 'COD'), ('2', 'RAZORPAY')], max_length=200)),
                ('payment_status', models.BooleanField(default=False)),
                ('delivery_status', models.CharField(choices=[('P', 'Pending'), ('S', 'Shipped'), ('D', 'Deliverd')], default='P', max_length=200)),
                ('status', models.BooleanField(default=True)),
                ('order_at', models.DateTimeField(auto_now_add=True)),
                ('order_id', models.CharField(default=None, max_length=200)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='product.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
