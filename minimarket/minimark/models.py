from django.db import models

# Create your models here.

class Product(models.Model):
    product = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
