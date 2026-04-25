# inventory/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from workshop.models import JobCard, JobCardSpareItem
from .models import Category, Item, ConsumptionRecord

class InventorySignalTests(TestCase):
    """
    Automated Testing Suite for Inventory Stock Deltas.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='staff_test_signal', password='password123')
        self.category = Category.objects.create(name='Engine Parts')
        self.item = Item.objects.create(
            category=self.category,
            name='Engine Oil 5W30',
            average_stock=100,
            current_stock=50
        )
        self.jobcard = JobCard.objects.create(
            registration_number='DL10AB1234',
            brand_name='Honda',
            model_name='City',
            admitted_date=timezone.now().date(),
            mileage='50000'
        )

    def test_stock_deduction_on_create(self):
        JobCardSpareItem.objects.create(
            job_card=self.jobcard,
            spare_part_name='Engine Oil 5W30',
            quantity=5,
            unit_price=800
        )
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_stock, 45)

    def test_stock_correction_on_update(self):
        spare = JobCardSpareItem.objects.create(
            job_card=self.jobcard,
            spare_part_name='Engine Oil 5W30',
            quantity=5,
            unit_price=800
        )
        spare.quantity = 10
        spare.save()
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_stock, 40)

    def test_stock_restoration_on_delete(self):
        spare = JobCardSpareItem.objects.create(
            job_card=self.jobcard,
            spare_part_name='Engine Oil 5W30',
            quantity=5,
            unit_price=800
        )
        spare.delete()
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_stock, 50)

class InventoryViewTests(TestCase):
    """
    Tests for all Inventory Management Views.
    """
    def setUp(self):
        self.office_group, _ = Group.objects.get_or_create(name='Office')
        self.user = User.objects.create_user(username='office_user', password='password')
        self.user.groups.add(self.office_group)
        self.client = Client()
        self.client.login(username='office_user', password='password')
        
        self.category = Category.objects.create(name='Brakes')
        self.item = Item.objects.create(category=self.category, name='Brake Pad', current_stock=10)

    def test_inventory_manage_and_search(self):
        # 1. Dashboard
        response = self.client.get(reverse('inventory_manage'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Search
        response = self.client.get(reverse('inventory_manage'), {'q': 'Brakes'})
        self.assertContains(response, 'Brakes')
        
        # 3. Search miss
        response = self.client.get(reverse('inventory_manage'), {'q': 'GhostPart'})
        # Should not contain Brakes if it didn't match
        self.assertNotContains(response, 'Brake Pad')

    def test_category_crud(self):
        # Add Category
        response = self.client.post(reverse('inventory_add_category'), {'name': 'Suspension'})
        self.assertRedirects(response, reverse('inventory_manage'))
        self.assertTrue(Category.objects.filter(name='Suspension').exists())
        
        # Edit Category
        response = self.client.post(reverse('inventory_edit_category', args=[self.category.id]), {'name': 'Braking Systems'})
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Braking Systems')
        
        # Delete Category
        response = self.client.post(reverse('inventory_delete_category', args=[self.category.id]))
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())

    def test_item_management(self):
        # Detail view
        response = self.client.get(reverse('inventory_category_detail', args=[self.category.id]))
        self.assertContains(response, 'Brake Pad')
        
        # Add Item
        response = self.client.post(reverse('inventory_add_item', args=[self.category.id]), {
            'name': 'Brake Disc',
            'average_stock': 20,
            'current_stock': 5
        })
        self.assertTrue(Item.objects.filter(name='Brake Disc').exists())
        
        # Edit Item
        response = self.client.post(reverse('inventory_edit_item', args=[self.item.id]), {
            'name': 'Brake Pad Premium',
            'average_stock': 15,
            'current_stock': 12
        })
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Brake Pad Premium')
        
        # Delete Item
        response = self.client.post(reverse('inventory_delete_item', args=[self.item.id]))
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())

    def test_stock_restock_and_low_stock(self):
        # Restock list
        response = self.client.get(reverse('inventory_restock'))
        self.assertContains(response, 'Brake Pad')
        
        # Update Stock
        response = self.client.post(reverse('inventory_update_stock', args=[self.item.id]), {'current_stock': 50})
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_stock, 50)
        
        # Low Stock view
        # Create a low stock item
        Item.objects.create(category=self.category, name='Low Fluid', average_stock=10, current_stock=1)
        response = self.client.get(reverse('inventory_low_stock'))
        self.assertContains(response, 'Low Fluid')

    def test_consumption_history(self):
        ConsumptionRecord.objects.create(user=self.user, item=self.item, quantity=2)
        response = self.client.get(reverse('inventory_history'))
        self.assertContains(response, 'Brake Pad')
        self.assertContains(response, 'office_user')

    def test_get_methods(self):
        # inventory_home redirects to restock
        response = self.client.get(reverse('inventory_home'))
        self.assertRedirects(response, reverse('inventory_restock'))

        # delete_category GET (no POST body) → safe redirect, does NOT delete
        response = self.client.get(
            reverse('inventory_delete_category', args=[self.category.id])
        )
        self.assertRedirects(response, reverse('inventory_manage'))
        self.assertTrue(Category.objects.filter(id=self.category.id).exists())

        # add_item GET → redirect to category_detail (no template needed)
        response = self.client.get(
            reverse('inventory_add_item', args=[self.category.id])
        )
        self.assertRedirects(
            response,
            reverse('inventory_category_detail', args=[self.category.id])
        )

        # edit_item GET → redirect to category_detail
        response = self.client.get(
            reverse('inventory_edit_item', args=[self.item.id])
        )
        self.assertRedirects(
            response,
            reverse('inventory_category_detail', args=[self.item.category.id])
        )

        # delete_item GET → redirect to manage
        response = self.client.get(
            reverse('inventory_delete_item', args=[self.item.id])
        )
        self.assertRedirects(response, reverse('inventory_manage'))
        self.assertTrue(Item.objects.filter(id=self.item.id).exists())

        # inventory_restock with empty search
        response = self.client.get(reverse('inventory_restock'), {'q': ''})
        self.assertEqual(response.status_code, 200)

        # update_stock POST without next_url → redirect to restock
        response = self.client.post(
            reverse('inventory_update_stock', args=[self.item.id]),
            {'current_stock': 50}
        )
        self.assertRedirects(response, reverse('inventory_restock'))
        self.item.refresh_from_db()
        self.assertEqual(self.item.current_stock, 50)

        # update_stock POST with next_url → redirect to that url
        response = self.client.post(
            reverse('inventory_update_stock', args=[self.item.id]),
            {'current_stock': 25, 'next': reverse('inventory_manage')}
        )
        self.assertRedirects(response, reverse('inventory_manage'))
 