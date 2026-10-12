from django.test import TestCase
from django.db.models import F
from django.db import models
from django.db import IntegrityError, transaction
from .models import User, Product, Variant, Location, StockLevel, StockMovement
from .services import move_stock

# Create your tests here.

class MoveStockTest(TestCase):
    ## Test data generation
    def setUp(self):
        self.shop = Location.objects.create(name="Shop")
        self.warehouse = Location.objects.create(name="Warehouse")
        self.user = User.objects.create_user(username="tester", password="pass")

        product = Product.objects.create(
            name = "Basic Tee", category = "T-Shirts", standard_wholesale_price = 10, identifier="P001"
        )

        self.variant = Variant.objects.create(
            product=product, colour="Black", sku="P001-BLK"
        )

    ## Testing a receipt
    def test_receipt_stock_increase(self):
        move_stock(self.variant, 50, None, self.warehouse, "RECEIPT", self.user)

        level = StockLevel.objects.get(variant=self.variant, location=self.warehouse)
        self.assertEqual(level.quantity, 50)
        self.assertEqual(StockMovement.objects.count(), 1)

    ## Testing a transfer
    def test_transfer_stock_move_between_locations(self):
        move_stock(self.variant, 50, None, self.warehouse, "RECEIPT", self.user)
        move_stock(self.variant, 20, self.warehouse, self.shop, "TRANSFER", self.user)

        warehouse_level = StockLevel.objects.get(variant=self.variant, location=self.warehouse)
        shop_level = StockLevel.objects.get(variant=self.variant, location=self.shop)

        self.assertEqual(warehouse_level.quantity, 30)
        self.assertEqual(shop_level.quantity, 20)
        self.assertEqual(StockMovement.objects.count(), 2)

    ## Testing a sale
    def test_sale_stock_decrease(self):
        move_stock(self.variant, 50, None, self.shop, "RECEIPT", self.user)
        move_stock(self.variant, 2, self.shop, None, "SALE", self.user)

        level = StockLevel.objects.get(variant=self.variant, location=self.shop)
        self.assertEqual(level.quantity, 48)

    ## Testing insufficient stock
    def test_cannot_oversell(self):
            move_stock(self.variant, 10, None, self.shop, "RECEIPT", self.user)

            with self.assertRaises(ValueError):
                move_stock(self.variant, 999, self.shop, None, "SALE", self.user)

            # stock should be unchanged, not partially decremented
            level = StockLevel.objects.get(variant=self.variant, location=self.shop)
            self.assertEqual(level.quantity, 10)

    ## Testing rollback on failure
    def test_failed_movement_is_fully_rolled_back(self):
        move_stock(self.variant, 10, None, self.shop, "RECEIPT", self.user)

        with self.assertRaises(ValueError):
            move_stock(self.variant, 999, self.shop, None, "SALE", self.user)

        # no StockMovement should have been written for the failed attempt
        self.assertEqual(StockMovement.objects.filter(type="SALE").count(), 0)

    ## General testing
    def test_stock_level_matches_sum_of_movements(self):
        move_stock(self.variant, 50, None, self.warehouse, "RECEIPT", self.user)
        move_stock(self.variant, 20, self.warehouse, self.shop, "TRANSFER", self.user)
        move_stock(self.variant, 5, self.shop, None, "SALE", self.user)

        for level in StockLevel.objects.all():
            incoming = StockMovement.objects.filter(
                variant=level.variant, to_location=level.location
            ).aggregate(total=models.Sum("quantity"))["total"] or 0

            outgoing = StockMovement.objects.filter(
                variant=level.variant, from_location=level.location
            ).aggregate(total=models.Sum("quantity"))["total"] or 0

            self.assertEqual(level.quantity, incoming - outgoing)