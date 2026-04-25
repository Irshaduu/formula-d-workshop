from django.test import TestCase
from inventory.models import Category, Item
from workshop.models import JobCard, JobCardSpareItem
from datetime import date


class InventorySignalsTestCase(TestCase):
    """
    Tests for the Stock Delta Engine (inventory/signals.py).
    Verifies all three synchronisation scenarios.
    """

    def setUp(self):
        self.category = Category.objects.create(name='Consumables')
        # Item model fields: category, name, average_stock, current_stock, usage_count
        self.item_oil = Item.objects.create(
            category=self.category, name='Oil Filter', current_stock=10, average_stock=10
        )
        self.item_air = Item.objects.create(
            category=self.category, name='Air Filter', current_stock=10, average_stock=10
        )

        self.job = JobCard.objects.create(
            admitted_date=date.today(),
            brand_name='Toyota',
            model_name='Corolla',
            registration_number='KL01SIG1234'
        )

    # ------------------------------------------------------------------
    # Scenario B/C: New entry and quantity update
    # ------------------------------------------------------------------
    def test_stock_deduction_on_create(self):
        """Scenario C – creating a spare item deducts from warehouse."""
        JobCardSpareItem.objects.create(
            job_card=self.job, spare_part_name='Oil Filter', quantity=2
        )
        self.item_oil.refresh_from_db()
        self.assertEqual(self.item_oil.current_stock, 8)

    def test_stock_correction_on_quantity_update(self):
        """Scenario B – updating quantity only deducts the delta."""
        spare = JobCardSpareItem.objects.create(
            job_card=self.job, spare_part_name='Oil Filter', quantity=2
        )
        self.item_oil.refresh_from_db()
        self.assertEqual(self.item_oil.current_stock, 8)  # 10 - 2

        spare.quantity = 5
        spare.save()
        self.item_oil.refresh_from_db()
        self.assertEqual(self.item_oil.current_stock, 5)  # 8 - 3 (delta)

    # ------------------------------------------------------------------
    # Scenario A: Part rename (name change)
    # ------------------------------------------------------------------
    def test_stock_rename_scenario(self):
        """Scenario A – renaming a part restores old stock and deducts new."""
        spare = JobCardSpareItem.objects.create(
            job_card=self.job, spare_part_name='Oil Filter', quantity=2
        )
        self.item_oil.refresh_from_db()
        self.assertEqual(self.item_oil.current_stock, 8)

        spare.spare_part_name = 'Air Filter'
        spare.save()

        self.item_oil.refresh_from_db()
        self.item_air.refresh_from_db()
        self.assertEqual(self.item_oil.current_stock, 10)  # restored
        self.assertEqual(self.item_air.current_stock, 8)   # deducted

    # ------------------------------------------------------------------
    # Delete restores stock
    # ------------------------------------------------------------------
    def test_restore_stock_on_delete(self):
        """Deleting a spare item restores stock to the warehouse."""
        spare = JobCardSpareItem.objects.create(
            job_card=self.job, spare_part_name='Oil Filter', quantity=3
        )
        self.item_oil.refresh_from_db()
        self.assertEqual(self.item_oil.current_stock, 7)

        spare.delete()
        self.item_oil.refresh_from_db()
        self.assertEqual(self.item_oil.current_stock, 10)

    # ------------------------------------------------------------------
    # pre_save: DoesNotExist branch (fake PK)
    # ------------------------------------------------------------------
    def test_pre_save_does_not_exist(self):
        """track_old_quantity should set zeros when old instance not found."""
        spare = JobCardSpareItem(
            job_card=self.job, spare_part_name='Oil Filter', quantity=2
        )
        spare.pk = 999999  # fake PK – won't exist in DB
        from inventory.signals import track_old_quantity
        track_old_quantity(sender=JobCardSpareItem, instance=spare)
        self.assertEqual(spare._old_quantity, 0)
        self.assertIsNone(spare._old_name)
