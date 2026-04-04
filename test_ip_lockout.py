import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Set up Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formulad_workshop.settings')
django.setup()

from django.test import RequestFactory
from workshop.auth_views import admin_login_view, check_ip_lockout, record_login_failure
from workshop.models import FailedAttempt
from django.contrib.messages.storage.fallback import FallbackStorage

def test_ip_lockout():
    factory = RequestFactory()
    ip = '123.123.123.123'
    
    # 1. Clear any existing attempts for this IP
    FailedAttempt.objects.filter(ip_address=ip).delete()
    
    print(f"\n--- TESTING IP LOCKOUT FOR {ip} ---")
    
    request = factory.post('/admin-login/', {'username': 'attacker', 'password': 'wrongpassword'})
    request.META['REMOTE_ADDR'] = ip
    # Add messages support to request
    setattr(request, '_messages', FallbackStorage(request))
    
    # 2. Simulate 5 failures
    for i in range(5):
        print(f"Attempt {i+1}...")
        admin_login_view(request)
    
    # 3. Check if locked
    is_locked = check_ip_lockout(request)
    print(f"\nResult: Is IP {ip} locked? {is_locked}")
    
    if is_locked:
        print("✅ SUCCESS: IP-based lockout is working.")
    else:
        print("❌ FAILURE: IP-based lockout did not trigger.")

if __name__ == "__main__":
    test_ip_lockout()
