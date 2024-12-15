from .models import Refill
from django.db.models import Sum


def update_water_tank_after_refill(water_tank_instance, pk=None):

    # If pk is provided, you can use it for logging or any other purposes.
    if pk:
    
      refill_instances = Refill.objects.filter(water_tank=water_tank_instance)

    total_quantity_by_refill_id = (
        refill_instances.values('refill_id')
        .annotate(total_quantity=Sum('quantity'))
    )

    total_liters = 0
    for entry in total_quantity_by_refill_id:
        total_liters += entry['total_quantity'] * 20

    water_tank_instance.liters_refilled = total_liters
    water_tank_instance.current_content = (
        water_tank_instance.liters - total_liters
    )
    water_tank_instance.save()
