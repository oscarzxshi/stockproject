from django.contrib import admin
from .models import User, Product, Variant, StockLevel, StockMovement, Location

# Register your models here.

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Variant)
admin.site.register(Location)
admin.site.register(StockLevel)
admin.site.register(StockMovement)
