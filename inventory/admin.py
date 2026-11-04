from django.contrib import admin
from .models import User, Product, Variant, StockLevel, StockMovement, Location

# Register your models here.

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "identifier", "standard_wholesale_price")
    list_filter = ("category",)
    search_fields = ("name", "identifier")
    inlines = [VariantInline]


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("product", "colour", "sku")
    search_fields = ("sku", "product__name")

    
admin.site.register(Location)
admin.site.register(User)
admin.site.register(StockLevel)
admin.site.register(StockMovement)

