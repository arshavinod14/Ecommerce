import datetime
from django.db import models
from store.models import Account
from django.utils.text import slugify

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=250,unique=True)
    # slug = models.SlugField(unique=True, null=True, blank=True)
    offer = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.name)
    #     super().save(*args, **kwargs)


class SubCategory(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    # slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        unique_together = ('name', 'category')

    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = slugify(self.name)
    #     super().save(*args, **kwargs)
    
class Brand(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name


class Size(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    ]
    size = models.CharField(max_length=1, choices=SIZE_CHOICES)
    
    def __str__(self):
        return self.size

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    offer = models.PositiveIntegerField(default=0)
    stock = models.IntegerField()
    sizes = models.ManyToManyField(Size)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    image1 = models.ImageField(upload_to="ecom/image")
    image2 = models.ImageField(upload_to="ecom/image")
    image3 = models.ImageField(upload_to="ecom/image")
    image4 = models.ImageField(upload_to="ecom/image")


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    # valid_from = models.DateField()
    valid_to = models.DateField(default=timezone.now)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
class CartItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    applied_coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)
    discount = models.IntegerField(default=0)

class GuestCart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user_ref = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)


class Wishlist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_products')
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} added to wishlist"


@receiver(post_save, sender=CartItems)
def mymodel_pre_save(sender, instance, **kwargs):
    # Perform some actions on instance before it is saved to the database
    print("wwwwwwwwwwwwwwwwwwss:",instance.user)
    # instance.total_price = instance.unit_price*instance.quantity
    cart = CartItems.objects.filter(user=instance.user, product=instance.product).exclude(id=instance.id)
    print("qqqqqqqqqqqqqqqqqqqqqqqq",len(cart))
    if len(cart)>0:
        for i in cart:
            cart.update(quantity = i.quantity+instance.quantity)
            cart.update(total_price = i.unit_price*(i.quantity+instance.quantity))
        CartItems.objects.filter(id=instance.id).delete()
    


# @receiver(post_save, sender=CartItems)
# def mymodel_pre_save(sender, instance, **kwargs):
#     # Perform some actions on instance before it is saved to the database
#     print("zzzzzzzzzzz:",instance.user)
#     cart = CartItems.objects.filter(user=instance.user,product = instance.product)

    

    # code = models.CharField(max_length=50, unique=True)
    # offer = models.IntegerField(validators=[MinValueValidator(1)])
    # end = models.DateTimeField(default=None)
    # discount = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])




#     def is_valid(self):
#         """
#         Check if the coupon is valid based on its valid_from and valid_to dates.
#         """
#         today = datetime.timezone.now().date()
#         return self.valid_from <= today <= self.valid_to

#     def is_applicable(self, amount):
#         """
#         Check if the coupon is applicable based on the minimum purchase amount requirement.
#         """
#         return amount >= self.min_purchase_amount

#     def calculate_discount(self, amount):
#         """
#         Calculate the discount amount based on the coupon's discount percentage.
#         """
#         return (self.discount / 100) * amount

    # def is_expired(self):
    #     """
    #     Check if the coupon is expired based on its valid_to date.
    #     """
    #     today = datetime.timezone.now().date()
    #     return today > self.valid_to