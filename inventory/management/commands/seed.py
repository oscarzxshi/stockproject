from django.core.management.base import BaseCommand
from inventory.models import Product, Variant, Location, User

import random
from django.core.management.base import BaseCommand
from inventory.models import User, Product, Variant, Location, StockLevel, StockMovement


COLOURS = ["Black", "White", "Navy", "Grey", "Olive"]
CATEGORIES = ["T-Shirts", "Hoodies", "Jeans", "Jackets", "Shirts"]


class Command(BaseCommand):
    help = "Populate the database with sample data"

    def handle(self, *args, **options):
        # Locations
        warehouse, _ = Location.objects.get_or_create(name="Warehouse")
        shop, _ = Location.objects.get_or_create(name="Shop")

        # Users, one per role
        admin, _ = User.objects.get_or_create(username="admin", defaults={"role": User.Role.ADMIN})
        admin.set_password("password123")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        warehouse_user, _ = User.objects.get_or_create(username="warehouse_staff", defaults={"role": User.Role.WAREHOUSE})
        warehouse_user.set_password("password123")
        warehouse_user.save()

        shop_user, _ = User.objects.get_or_create(username="shop_staff", defaults={"role": User.Role.SHOP})
        shop_user.set_password("password123")
        shop_user.save()

        # Products and variants
        variant_count = 0
        for i in range(1, 11):
            product, _ = Product.objects.get_or_create(
                identifier=f"P{i:03}",
                defaults={
                    "name": f"{random.choice(['Basic', 'Classic', 'Relaxed', 'Slim'])} {random.choice(CATEGORIES)[:-1]}",
                    "category": random.choice(CATEGORIES),
                    "standard_wholesale_price": round(random.uniform(8, 35), 2),
                },
            )

            for colour in random.sample(COLOURS, k=4):
                sku = f"{product.identifier}-{colour[:3].upper()}"
                variant, created = Variant.objects.get_or_create(
                    product=product, colour=colour, defaults={"sku": sku},
                )
                variant_count += 1

                if created:
                    # Receive stock into the warehouse
                    qty = random.randint(20, 100)
                    StockMovement.objects.create(
                        type=StockMovement.Type.RECEIPT,
                        from_location=None,
                        to_location=warehouse,
                        user=admin,
                        quantity=qty,
                    )
                    level, _ = StockLevel.objects.get_or_create(variant=variant, location=warehouse, defaults={"quantity": 0})
                    level.quantity += qty
                    level.save()

                    # Transfer some to the shop
                    transfer_qty = random.randint(5, min(20, qty))
                    StockMovement.objects.create(
                        type=StockMovement.Type.TRANSFER,
                        from_location=warehouse,
                        to_location=shop,
                        user=warehouse_user,
                        quantity=transfer_qty,
                    )
                    level.quantity -= transfer_qty
                    level.save()

                    shop_level, _ = StockLevel.objects.get_or_create(variant=variant, location=shop, defaults={"quantity": 0})
                    shop_level.quantity += transfer_qty
                    shop_level.save()

        self.stdout.write(self.style.SUCCESS(
            f"Seeded 2 locations, 10 products, {variant_count} variants, 3 users."
        ))