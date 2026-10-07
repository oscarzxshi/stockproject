from django.db import transaction
from django.db.models import F
from .models import StockLevel, StockMovement

@transaction.atomic
def move_stock(variant, qty, from_loc, to_loc, mtype, user, ref=""):
    if from_loc:
        level = StockLevel.objects.select_for_update().get(variant=variant, location=from_loc)
        if level.quantity < qty:
            raise ValueError("Insufficient stock")          # ← a rule, not a DB operation
        level.quantity = F("quantity") - qty
        level.save()
    if to_loc:
        level, _ = StockLevel.objects.select_for_update().get_or_create(variant=variant, location=to_loc)
        level.quantity = F("quantity") + qty
        level.save()
    StockMovement.objects.create(variant=variant, from_location=from_loc,
        to_location=to_loc, quantity=qty, type=mtype, user=user, reference=ref)

