from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Item(models.Model):
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
        if self.average_stock <= 0:
            return 100 # Default to full/green if no average set
        return (self.current_stock / self.average_stock) * 100

    def stock_status_color(self):
        pct = self.stock_percentage()
        if pct < 25:
            return "#ef4444" # Red
        elif pct < 50:
            return "#eab308" # Yellow
        else:
            return "#22c55e" # Green

class ConsumptionRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.FloatField()
    date = models.DateField(default=timezone.now)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item.name} ({self.quantity})"
