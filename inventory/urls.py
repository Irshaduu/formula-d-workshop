from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventory_home, name='inventory_home'),
    path('manage/', views.inventory_manage, name='inventory_manage'),
    
    # Category Management
    path('category/<int:category_id>/', views.category_detail, name='inventory_category_detail'),
    path('category/add/', views.add_category, name='inventory_add_category'),
    path('category/edit/<int:category_id>/', views.edit_category, name='inventory_edit_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='inventory_delete_category'),
    
    # Item Management
    path('category/<int:category_id>/item/add/', views.add_item, name='inventory_add_item'),
    path('item/edit/<int:item_id>/', views.edit_item, name='inventory_edit_item'),
    path('item/delete/<int:item_id>/', views.delete_item, name='inventory_delete_item'),
    
    # Restock & Low Stock
    path('restock/', views.inventory_restock, name='inventory_restock'),
    path('restock/update/<int:item_id>/', views.update_stock, name='inventory_update_stock'),
    path('low-stock/', views.inventory_low_stock, name='inventory_low_stock'),
    path('history/', views.consumption_history, name='inventory_history'),
]
