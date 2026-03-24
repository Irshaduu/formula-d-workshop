from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from workshop.models import JobCardSpareItem
from .models import Item

@receiver(pre_save, sender=JobCardSpareItem)
def track_old_quantity(sender, instance, **kwargs):
    """Store the old quantity and name before a save occurs to calculate stock deltas."""
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
    """Adjust inventory stock based on the delta between old and new quantites."""
    new_qty = float(instance.quantity or 0)
    new_name = instance.spare_part_name
    
    old_qty = float(getattr(instance, '_old_quantity', 0))
    old_name = getattr(instance, '_old_name', None)

    # Scenario 1: Name changed (we must restore old and deduct new)
    if old_name and old_name != new_name:
        
        # Restore old item stock 
        old_inv_item = Item.objects.filter(name__iexact=old_name).first()
        if old_inv_item:
            old_inv_item.current_stock += old_qty
            old_inv_item.save()
            
        # Deduct new item stock
        if new_name:
            new_inv_item = Item.objects.filter(name__iexact=new_name).first()
            if new_inv_item:
                new_inv_item.current_stock -= new_qty
                new_inv_item.save()
                
    # Scenario 2: Name stayed the same, just adjust the quantity difference
    elif new_name:
        diff = new_qty - old_qty
        if diff != 0:
            inv_item = Item.objects.filter(name__iexact=new_name).first()
            if inv_item:
                inv_item.current_stock -= diff
                inv_item.save()

@receiver(post_delete, sender=JobCardSpareItem)
def restore_stock_on_delete(sender, instance, **kwargs):
    """Restore stock if a spare part is deleted from a job card."""
    if instance.spare_part_name and instance.quantity:
        inv_item = Item.objects.filter(name__iexact=instance.spare_part_name).first()
        if inv_item:
            inv_item.current_stock += float(instance.quantity)
            inv_item.save()
