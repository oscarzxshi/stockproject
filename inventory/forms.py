from django import forms
from django.forms import inlineformset_factory
from .models import Product, Variant, Location, StockMovement, User


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

class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            is_select = isinstance(field.widget, forms.Select)
            field.widget.attrs["class"] = "form-select" if is_select else "form-control"


class ReceiveForm(BootstrapMixin, forms.Form):
    variant = forms.ModelChoiceField(queryset=Variant.objects.select_related("product"))
    location = forms.ModelChoiceField(queryset=Location.objects.all(), label="Received into")
    quantity = forms.IntegerField(min_value=1)
    reference = forms.CharField(
        max_length=100, required=False, label="Reference",
        help_text="Optional, e.g. a delivery note or supplier order number.",
    )

class SaleForm(BootstrapMixin, forms.Form):
    variant = forms.ModelChoiceField(queryset=Variant.objects.select_related("product"))
    location = forms.ModelChoiceField(queryset=Location.objects.all(), label="Sold from")
    quantity = forms.IntegerField(min_value=1)
    reference = forms.CharField(max_length=100, required=False)


class AdjustmentForm(BootstrapMixin, forms.Form):
    DIRECTIONS = [("ADD", "Add stock (found, correction)"), ("REMOVE", "Remove stock (damage, loss)")]

    variant = forms.ModelChoiceField(queryset=Variant.objects.select_related("product"))
    location = forms.ModelChoiceField(queryset=Location.objects.all())
    direction = forms.ChoiceField(choices=DIRECTIONS)
    quantity = forms.IntegerField(min_value=1)
    reason = forms.CharField(max_length=100)


class TransferForm(BootstrapMixin, forms.Form):
    variant = forms.ModelChoiceField(queryset=Variant.objects.select_related("product"))
    from_location = forms.ModelChoiceField(queryset=Location.objects.all())
    to_location = forms.ModelChoiceField(queryset=Location.objects.all())
    quantity = forms.IntegerField(min_value=1)

    def clean(self):
        data = super().clean()
        if data.get("from_location") and data.get("from_location") == data.get("to_location"):
            raise forms.ValidationError("Choose two different locations.")
        return data

class MovementFilterForm(BootstrapMixin, forms.Form):
    variant = forms.ModelChoiceField(
        queryset=Variant.objects.select_related("product"), required=False, empty_label="All variants")
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(), required=False, empty_label="All locations")
    type = forms.ChoiceField(
        choices=[("", "All types")] + StockMovement.Type.choices, required=False)
    user = forms.ModelChoiceField(
        queryset=User.objects.all(), required=False, empty_label="All users")
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

