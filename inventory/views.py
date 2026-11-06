from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Sum
from .models import Product, Variant, StockLevel, StockMovement
from .forms import ProductForm, VariantFormSet

# Create your views here.

def index(request):
    return render(request, "inventory/layout.html") 

class StaffLoginView(LoginView):
    template_name = "inventory/login.html"

@login_required
def products(request):
    products = Product.objects.prefetch_related("variants").order_by("category", "name")
    return render(request, "inventory/products.html", {"products": products})

@login_required
def add_product(request):
    if request.user.role not in ("ADMIN", "WAREHOUSE"):
        messages.error(request, "You don't have permission to add products.")
        return redirect("products")

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            formset = VariantFormSet(request.POST, instance=product)
            if formset.is_valid():
                formset.save()
                messages.success(request, f"{product.name} added.")
                return redirect("products")
        else:
            formset = VariantFormSet(request.POST)
    else:
        form = ProductForm()
        formset = VariantFormSet()

    return render(request, "inventory/add_product.html", {"form": form, "formset": formset})

@login_required
def product_detail(request, product_id):
    variants = Variant.objects.annotate(
        total_stock=Sum("stock_level__quantity")
    ).prefetch_related(
        Prefetch("stock_level", queryset=StockLevel.objects.select_related("location"))
    )
    product = get_object_or_404(
        Product.objects.prefetch_related(Prefetch("variants", queryset=variants)),
        pk=product_id,
    )
    return render(request, "inventory/product_detail.html", {"product": product})

