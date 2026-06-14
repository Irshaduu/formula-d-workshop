from django.urls import path
from . import views
from . import views_suppliers

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
    path('list/', views.inventory_list, name='inventory_list'),
    path('restock/update/<int:item_id>/', views.update_stock, name='inventory_update_stock'),
    path('low-stock/', views.inventory_low_stock, name='inventory_low_stock'),
    path('history/', views.consumption_history, name='inventory_history'),
    # Supplier Shops
    path('shops/', views_suppliers.supplier_shop_list, name='supplier_shop_list'),
    path('shops/deactivated/', views_suppliers.deactivated_supplier_shop_list, name='deactivated_supplier_shop_list'),
    path('shops/add/', views_suppliers.add_supplier_shop, name='add_supplier_shop'),
    path('shops/<int:shop_id>/', views_suppliers.supplier_shop_detail, name='supplier_shop_detail'),
    path('shops/<int:shop_id>/edit/', views_suppliers.edit_supplier_shop, name='edit_supplier_shop'),
    path('shops/<int:shop_id>/deactivate/', views_suppliers.deactivate_supplier_shop, name='deactivate_supplier_shop'),
    path('shops/<int:shop_id>/activate/', views_suppliers.activate_supplier_shop, name='activate_supplier_shop'),
    
    # Shop Catalogs & Restocking
    path('shops/<int:shop_id>/catalog/add/', views_suppliers.add_shop_catalog_item, name='add_shop_catalog_item'),
    path('shops/<int:shop_id>/catalog/<int:catalog_item_id>/remove/', views_suppliers.remove_shop_catalog_item, name='remove_shop_catalog_item'),
    path('shops/<int:shop_id>/catalog/<int:catalog_item_id>/edit/', views_suppliers.edit_catalog_item, name='edit_catalog_item'),
    path('shops/<int:shop_id>/restock/', views_suppliers.shop_restock_select, name='shop_restock_select'),
    path('shops/<int:shop_id>/restock/bill/', views_suppliers.shop_restock_bill, name='shop_restock_bill'),
    path('shops/<int:shop_id>/bill/<int:bill_id>/edit/', views_suppliers.edit_restock_bill, name='edit_restock_bill'),
    path('shops/<int:shop_id>/bill/<int:bill_id>/delete/', views_suppliers.delete_restock_bill, name='delete_restock_bill'),
    path('shops/<int:shop_id>/bill/<int:bill_id>/discount/', views_suppliers.update_bill_discount, name='update_bill_discount'),
    
    # Shop Payments
    path('shops/<int:shop_id>/payment/add/', views_suppliers.add_shop_payment, name='add_shop_payment'),
    path('shops/<int:shop_id>/payment/<int:payment_id>/delete/', views_suppliers.delete_shop_payment, name='delete_shop_payment'),
    
    # AJAX Pagination
    path('shops/<int:shop_id>/bills/ajax/', views_suppliers.ajax_supplier_bills, name='ajax_supplier_bills'),
    path('shops/<int:shop_id>/payments/ajax/', views_suppliers.ajax_supplier_payments, name='ajax_supplier_payments'),
    
    # Item Suppliers View
    path('item/<int:item_id>/suppliers/', views_suppliers.inventory_item_suppliers, name='inventory_item_suppliers'),
]
