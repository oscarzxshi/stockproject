from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "admin"
        WAREHOUSE = "WAREHOUSE", "Warehouse staff"
        SHOP = "SHOP", "Shop staff"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SHOP)

    def __str__(self):
        return self.username

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    standard_wholesale_price = models.DecimalField(max_digits=8, decimal_places=2)
    identifier = models.CharField(max_length=10, unique=True)

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    colour = models.CharField(max_length=50)
    sku = models.CharField(max_length=50, unique=True)

class Location(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class StockLevel(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="stock_level")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="stock_level")
    quantity = models.PositiveIntegerField(default=0)

class StockMovement(models.Model):
    class Type(models.TextChoices):
        RECEIPT = "RECEIPT", "receipt"
        TRANSFER = "TRANSFER", "transfer"
        SALE = "SALE", "sale"

    type = models.CharField(max_length=50, choices=Type.choices, default=Type.RECEIPT)

    from_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="sent", null=True, blank=True)
    to_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="received", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="movement_created")
    quantity = models.DecimalField(max_digits=6, decimal_places=0)
    timestamp = models.DateTimeField(auto_now_add=True)

