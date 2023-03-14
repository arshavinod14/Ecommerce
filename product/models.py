import datetime
from django.db import models
from store.models import Account
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=250)
    offer = models.PositiveIntegerField()
    def __str__(self):
        return self.name

class SubCategory(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)

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
    brand = models.CharField(max_length=200)
    image1 = models.ImageField(upload_to="ecom/image")
    image2 = models.ImageField(upload_to="ecom/image")
    image3 = models.ImageField(upload_to="ecom/image")
    image4 = models.ImageField(upload_to="ecom/image")



class CartItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    unit_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=50, decimal_places=2, null=True)
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)


