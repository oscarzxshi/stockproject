from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from .models import Product
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