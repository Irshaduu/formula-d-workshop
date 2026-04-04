from django.test import TestCase
from django.contrib.auth.models import User, Group
from .templatetags.auth_extras import has_group

class TemplateTagTests(TestCase):
    """
    Tests for workshop extra template tags.
    """

    def setUp(self):
        self.owner_group = Group.objects.create(name='Owner')
        self.user = User.objects.create_user(username='tester', password='password')
        self.superuser = User.objects.create_superuser(username='super', password='password', email='s@s.com')
        self.guest = User.objects.create_user(username='guest', password='password')

    def test_has_group_filter(self):
        # 1. Negative Case (No Group)
        self.assertFalse(has_group(self.user, 'Owner'))
        
        # 2. Positive Case (Group member)
        self.user.groups.add(self.owner_group)
        self.assertTrue(has_group(self.user, 'Owner'))
        
        # 3. Superuser (True for everything)
        self.assertTrue(has_group(self.superuser, 'Owner'))
        self.assertTrue(has_group(self.superuser, 'RandomGroup'))
        
        # 4. Unauthenticated user
        from django.contrib.auth.models import AnonymousUser
        anon = AnonymousUser()
        self.assertFalse(has_group(anon, 'Owner'))
        
        # 5. Non-existent group
        self.assertFalse(has_group(self.user, 'GhostGroup'))
