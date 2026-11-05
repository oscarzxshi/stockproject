from django import forms
from django.forms import inlineformset_factory
from .models import Product, Variant


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "category", "standard_wholesale_price", "identifier"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "standard_wholesale_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "identifier": forms.TextInput(attrs={"class": "form-control"}),
        }


VariantFormSet = inlineformset_factory(
    Product,
    Variant,
    fields=["colour", "sku"],
    extra=1,
    can_delete=False,
    widgets={
        "colour": forms.TextInput(attrs={"class": "form-control"}),
        "sku": forms.TextInput(attrs={"class": "form-control"}),
    },
)
