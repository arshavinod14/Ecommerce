from django.db import models
from product.models import Size

def insert_sizes():
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    ]
    for size in SIZE_CHOICES:
        Size.objects.create(size=size[0])

insert_sizes()