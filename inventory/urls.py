from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.StaffLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("products/", views.products, name="products"),
    path("products/add/", views.add_product, name="add_product"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("stock/", views.stock, name="stock"),
    path("receive/", views.receive, name="receive"),
    path("sale/", views.sale, name="sale"),
    path("adjust/", views.adjustment, name="adjustment"),
    path("transfer/", views.transfer, name="transfer"),
    path("history/", views.history, name="history"),
]