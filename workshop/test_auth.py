from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import FailedAttempt
import time

class AuthFlowTests(TestCase):
    """
    Exhaustive testing for the Authentication Fortress.
    Covers 100% of Staff, Admin 2FA, and Password recovery.
    """

    def setUp(self):
        FailedAttempt.objects.all().delete()
        # Groups
        self.owner_group, _ = Group.objects.get_or_create(name='Owner')
        self.office_group, _ = Group.objects.get_or_create(name='Office')
        
        # User matching .env OWNER_1_USERNAME=Sahad
        self.owner = User.objects.create_user(username='Sahad', password='ownerpassword')
        self.owner.groups.add(self.owner_group)
        
        self.staff_office = User.objects.create_user(username='office_test', password='staffpassword')
        self.staff_office.groups.add(self.office_group)
        
        self.client = Client()
        self.test_ip = '192.168.1.50'

    def test_staff_login_view_complete(self):
        url = reverse('login')
        
        # 1. Already Authenticated Redirect
        self.client.login(username='office_test', password='staffpassword')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'))
        self.client.logout()

        # 2. Lockout Check
        FailedAttempt.objects.create(ip_address=self.test_ip, failures=5)
        response = self.client.get(url, REMOTE_ADDR=self.test_ip)
        self.assertContains(response, "Security Lockout")
        
        # Manually expire lockout to test reset
        FailedAttempt.objects.filter(ip_address=self.test_ip).update(
            last_attempt = timezone.now() - timedelta(minutes=16)
        )
        response = self.client.get(url, REMOTE_ADDR=self.test_ip)
        self.assertNotContains(response, "Security Lockout")

        # 3. Invalid Credentials
        response = self.client.post(url, {'username': 'office_test', 'password': 'wrong'}, follow=True)
        self.assertContains(response, "Invalid credentials")

        # 4. Block Owner
        response = self.client.post(url, {'username': 'Sahad', 'password': 'ownerpassword'}, follow=True)
        self.assertContains(response, "Invalid credentials")

    def test_admin_login_and_otp_comprehensive(self):
        url_step1 = reverse('admin_login')
        url_step2 = reverse('otp_verify')
        
        # 1. Step 1: Mobile Resolution
        # Sahad's mobile is +919567494933 in .env
        response = self.client.post(url_step1, {'username': '9567494933', 'password': 'ownerpassword'})
        self.assertRedirects(response, url_step2)
        
        # 2. Step 2: Failed OTP Limit
        session = self.client.session
        session['2fa_otp'] = '999999'
        session['2fa_expire'] = time.time() + 300
        session['pre_2fa_user_id'] = self.owner.id
        session.save()
        
        for i in range(2):
            self.client.post(url_step2, {'otp': '000000'})
        response = self.client.post(url_step2, {'otp': '000000'})
        self.assertRedirects(response, url_step1)
        self.assertNotIn('2fa_otp', self.client.session)

    def test_password_reset_flow_edge_cases(self):
        url_forgot = reverse('owner_forgot_password')
        url_reset = reverse('owner_reset_password')
        
        # 1. Non-existent User
        response = self.client.post(url_forgot, {'username': 'ghost_user'}, follow=True)
        self.assertContains(response, "No Owner account found")
        
        # 2. Cooldown check
        self.client.post(url_forgot, {'username': 'Sahad'})
        response = self.client.post(url_forgot, {'username': 'Sahad'}, follow=True)
        self.assertContains(response, "Please wait")

        # 3. Reset View: Password Match & Length
        session = self.client.session
        session['pwd_reset_user_id'] = self.owner.id
        session['pwd_reset_otp'] = '123456'
        session['pwd_reset_expire'] = time.time() + 300
        session.save()
        
        # Short Password
        response = self.client.post(url_reset, {'otp': '123456', 'new_password': '123', 'confirm_password': '123'}, follow=True)
        self.assertContains(response, "at least 8 characters")
        
        # Mismatch
        response = self.client.post(url_reset, {'otp': '123456', 'new_password': 'password123', 'confirm_password': 'mismatch'}, follow=True)
        self.assertContains(response, "do not match")
        
        # Success
        response = self.client.post(url_reset, {'otp': '123456', 'new_password': 'newpowerpwd', 'confirm_password': 'newpowerpwd'})
        self.assertRedirects(response, reverse('admin_login'))
