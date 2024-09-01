from django.db import models


class Product(models.Model):
    product_id = models.CharField(max_length=100, unique=True)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.FloatField()
    quantity_sold = models.IntegerField()
    rating = models.FloatField()
    review_count = models.IntegerField()
