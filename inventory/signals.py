from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from workshop.models import JobCardSpareItem
from .models import Item

@receiver(pre_save, sender=JobCardSpareItem)
def track_old_quantity(sender, instance, **kwargs):
    """
    Snapshots the original part data before a database commit.
    This is critical for calculating stock deltas during updates.
    """
    if instance.pk:
        try:
            old_instance = JobCardSpareItem.objects.get(pk=instance.pk)
            instance._old_quantity = old_instance.quantity or 0
            instance._old_name = old_instance.spare_part_name
        except JobCardSpareItem.DoesNotExist:
            instance._old_quantity = 0
            instance._old_name = None
    else:
        instance._old_quantity = 0
        instance._old_name = None

@receiver(post_save, sender=JobCardSpareItem)
def update_stock_on_save(sender, instance, created, **kwargs):
    """
    Orchestrates the Workshop-to-Warehouse stock synchronization.
    
    Algorithm Breakdown (Delta Logic):
    ---------------------------------
    Scenario A: Part Replacement (Name Change)
        If 'Oil Filter' is changed to 'Air Filter':
        1. Restore stock for 'Oil Filter' (+OldQty).
        2. Deduct stock for 'Air Filter' (-NewQty).
        
    Scenario B: Quantity Adjustment (Same Name)
        If 'Oil Filter' remains but quantity goes from 2 to 5:
        1. Calculate Delta: 5 - 2 = 3.
        2. Deduct only the difference (-3) from Warehouse.
        
    Scenario C: New Entry
        1. Deduct full quantity from Warehouse.
    """
    new_qty = float(instance.quantity or 0)
    new_name = instance.spare_part_name
    
    old_qty = float(getattr(instance, '_old_quantity', 0))
    old_name = getattr(instance, '_old_name', None)

    # Logic Implementation...
    if old_name and old_name != new_name:
        # Scenario A: Rename
        old_inv_item = Item.objects.filter(name__iexact=old_name).first()
        if old_inv_item:
            old_inv_item.current_stock += old_qty
            old_inv_item.save()
            
        if new_name:
            new_inv_item = Item.objects.filter(name__iexact=new_name).first()
            if new_inv_item:
                new_inv_item.current_stock -= new_qty
                new_inv_item.save()
                
    elif new_name:
        # Scenario B/C: Quantity Change
        diff = new_qty - old_qty
        if diff != 0:
            inv_item = Item.objects.filter(name__iexact=new_name).first()
            if inv_item:
                inv_item.current_stock -= diff
                inv_item.save()

@receiver(post_delete, sender=JobCardSpareItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    """
    Reverses stock deduction when a part is removed from a job card.
    Ensure 100% warehouse integrity on cancellations.
    """
    if instance.spare_part_name and instance.quantity:
        inv_item = Item.objects.filter(name__iexact=instance.spare_part_name).first()
        if inv_item:
            inv_item.current_stock += float(instance.quantity)
            inv_item.save()
