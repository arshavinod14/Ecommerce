from django.utils import timezone
from django.db import models
from store.models import Account,Address
from product.models import Product
# Create your models here.



class Order(models.Model):
    payment_choice = (("1", "COD"),("2", "RAZORPAY"))
        # ("3", "PAYPAL"),)

    delivery_status_choice =(("P","Pending"),("S","Shipped"),("D","Deliverd"),("C","Cancelled"))

    user = models.ForeignKey(Account, on_delete=models.PROTECT)
    total_price = models.DecimalField(max_digits=6, decimal_places=2)
    payment_id = models.CharField(max_length=200, null=True)
    payment_method = models.CharField(max_length=200, choices=payment_choice)
    payment_status = models.BooleanField(default=False)
    delivery_status = models.CharField(max_length=200, choices=delivery_status_choice, default="P")
    status = models.BooleanField(default=True)
    order_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=200, default=None)
    address = models.ForeignKey(Address, related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)



class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=120)
    payment_method = models.CharField(max_length=120)
    amount_paid = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=200, default=None, unique=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_price = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    quantity = models.PositiveIntegerField()

    def get_total_price(self):
        return self.product_price * self.quantity


    