from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from .models import Mechanic, UserSession
from django.contrib.sessions.models import Session

class ManagementViewTests(TestCase):
    """
    Tests for the HQ Command Center (management_views.py).
    Titan Standard 100% Verification.
    """

    def setUp(self):
        self.owner_group, _ = Group.objects.get_or_create(name='Owner')
        self.office_group, _ = Group.objects.get_or_create(name='Office')
        
        self.owner = User.objects.create_user(username='Sahad', password='password')
        self.owner.groups.add(self.owner_group)
        
        self.staff = User.objects.create_user(username='staff_user', password='password')
        self.staff.groups.add(self.office_group)
        
        self.client = Client()
        self.client.login(username='Sahad', password='password')
        
    def test_manage_dashboard_sections(self):
        url = reverse('manage_dashboard')
        # All sections
        for section in ['accounts', 'workshop', 'security', 'inventory']:
            response = self.client.get(url, {'section': section})
            self.assertEqual(response.status_code, 200)

    def test_mechanic_management(self):
        # 1. Add
        response = self.client.post(reverse('manage_mechanic_add'), {'name': 'New Mech'})
        self.assertTrue(Mechanic.objects.filter(name='New Mech').exists())
        
        # 2. Rename
        mech = Mechanic.objects.create(name='Old Mech')
        response = self.client.post(reverse('manage_mechanic_rename', args=[mech.id]), {'name': 'Renamed Mech'})
        mech.refresh_from_db()
        self.assertEqual(mech.name, 'Renamed Mech')
        
        # 3. Delete
        response = self.client.post(reverse('manage_mechanic_delete', args=[mech.id]))
        self.assertFalse(Mechanic.objects.filter(id=mech.id).exists())

    def test_session_revocation_realtime(self):
        # 1. Create a fake session to revoke
        # UserSession needs a valid session_key
        session = Session.objects.create(session_data='', expire_date=timezone.now())
        user_session = UserSession.objects.create(
            user=self.staff,
            session_key=session.session_key,
            ip_address='127.0.0.1'
        )
        
        url = reverse('manage_terminate_session', args=[user_session.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('manage_dashboard') + '?section=security')
        
        # Verify both are gone
        self.assertFalse(UserSession.objects.filter(pk=user_session.pk).exists())
        self.assertFalse(Session.objects.filter(session_key=session.session_key).exists())
