from django.contrib import admin
from .models import Category, Item, ConsumptionRecord

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'current_stock', 'average_stock', 'usage_count')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(ConsumptionRecord)
class ConsumptionRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'date')
    list_filter = ('date', 'user')
