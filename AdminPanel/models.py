from django.db import models

# Create your models here.
class Banner(models.Model):
    title1 = models.CharField(max_length=120)
    title2 = models.CharField(max_length=120)
    image1 = models.ImageField(upload_to="ecom/image")
    tag = models.CharField(max_length=120)


