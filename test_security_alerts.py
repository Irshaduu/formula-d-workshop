import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Set up Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formulad_workshop.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from django.test import RequestFactory
from decouple import config
from workshop.auth_views import send_owner_login_alert

def test_alerts():
    factory = RequestFactory()
    request = factory.get('/')
    request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
    request.META['REMOTE_ADDR'] = '192.168.1.55'

    owner1_u = config('OWNER_1_USERNAME', default='sahad').strip()
    owner2_u = config('OWNER_2_USERNAME', default='rijas').strip()

    print(f"\n--- TESTING ALERT: {owner1_u} LOGGING IN ---")
    u1 = User(username=owner1_u)
    send_owner_login_alert(u1, request)

    print(f"\n--- TESTING ALERT: {owner2_u} LOGGING IN ---")
    u2 = User(username=owner2_u)
    send_owner_login_alert(u2, request)

if __name__ == "__main__":
    test_alerts()
