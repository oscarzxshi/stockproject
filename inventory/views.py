from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Prefetch, Sum
from .models import Product, Variant, StockLevel, StockMovement, Location
from .forms import ProductForm, VariantFormSet, SaleForm, AdjustmentForm, TransferForm
from .services import move_stock

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

@login_required
def stock(request):
    locations = Location.objects.order_by("name")

    location = None
    location_id = request.GET.get("location", "")
    if location_id.isdigit():
        location = locations.filter(pk=location_id).first()
    if location is None:
        location = locations.first()

    levels = StockLevel.objects.none()
    if location:
        levels = (
            StockLevel.objects.filter(location=location)
            .select_related("variant__product")
            .order_by("variant__product__name", "variant__colour")
        )

    page_obj = Paginator(levels, 20).get_page(request.GET.get("page"))

    return render(request, "inventory/stock.html", {
        "locations": locations,
        "location": location,
        "page_obj": page_obj,
    })

def _form_page(request, form, title, button):
    return render(request, "inventory/stock_form.html", {"form": form, "title": title, "button": button})

def _apply(form, **move):
    """Run move_stock, turning failures into a form error. Returns True on success."""
    try:
        move_stock(**move)
    except ValueError as e:
        form.add_error(None, str(e))
    except StockLevel.DoesNotExist:
        form.add_error(None, "There is no stock of this item at that location.")
    else:
        return True
    return False

@login_required
def sale(request):
    form = SaleForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        if _apply(form, variant=d["variant"], qty=d["quantity"], from_loc=d["location"], to_loc=None,
                  mtype=StockMovement.Type.SALE, user=request.user, ref=d["reference"]):
            messages.success(request, f"Sold {d['quantity']} x {d['variant']}.")
            return redirect("sale")
    return _form_page(request, form, "Record a sale", "Record sale")

@login_required
def adjustment(request):
    form = AdjustmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        adding = d["direction"] == "ADD"
        if _apply(form, variant=d["variant"], qty=d["quantity"],
                  from_loc=None if adding else d["location"], to_loc=d["location"] if adding else None,
                  mtype=StockMovement.Type.ADJUSTMENT, user=request.user, ref=d["reason"]):
            messages.success(request, "Stock adjusted.")
            return redirect("adjustment")
    return _form_page(request, form, "Adjust stock", "Save adjustment")

@login_required
def transfer(request):
    form = TransferForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        if _apply(form, variant=d["variant"], qty=d["quantity"], from_loc=d["from_location"],
                  to_loc=d["to_location"], mtype=StockMovement.Type.TRANSFER, user=request.user):
            messages.success(request, f"Moved {d['quantity']} x {d['variant']} to {d['to_location']}.")
            return redirect("transfer")
    return _form_page(request, form, "Transfer stock", "Transfer")