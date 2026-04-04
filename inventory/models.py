from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """
    Groups Inventory Items (e.g., Engine Parts, Fluids, Electrical).
    Used for navigation and bulk stock reporting.
    """
    name = models.CharField(max_length=100, db_index=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Item(models.Model):
    """
    A specific part or consumable in the workshop warehouse.
    
    Attributes:
        category (ForeignKey): Link to parent group.
        name (CharField): Part name (matches SparePart master list).
        average_stock (FloatField): Threshold for low-stock warnings.
        current_stock (FloatField): Real-time quantity on hand.
        usage_count (FloatField): Popularity score for smart-sorting.
    """
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    average_stock = models.FloatField(default=0, help_text="Ideal stock level for calculation")
    current_stock = models.FloatField(default=0)
    usage_count = models.FloatField(default=0, help_text="Cached popularity score (frequency of use)")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name'], 
                name='unique_category_item_idx'
            )
        ]
        ordering = ['-usage_count', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def stock_percentage(self):
        """Calculates health percentage for visual progress bars."""
        if self.average_stock <= 0:
            return 100 # Default to full/green if no average set
        return (self.current_stock / self.average_stock) * 100

    def stock_status_color(self):
        """Returns the Tailwind/Bootstrap compatible hex color for stock health."""
        pct = self.stock_percentage()
        if pct < 25:
            return "#ef4444" # Red (Critical)
        elif pct < 50:
            return "#eab308" # Yellow (Warning)
        else:
            return "#22c55e" # Green (Healthy)

class ConsumptionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.FloatField()
    date = models.DateField(default=timezone.now)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item.name} ({self.quantity})"
