import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

# Set up Django environment
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formulad_workshop.settings')
django.setup()

from django.test import RequestFactory
from workshop.auth_views import check_ip_lockout, record_login_failure
from workshop.models import FailedAttempt

def test_hardened_logic():
    factory = RequestFactory()
    ip = '123.123.123.123'
    
    # 1. Clear any existing attempts for this IP
    FailedAttempt.objects.filter(ip_address=ip).delete()
    
    print(f"\n--- TESTING LOGIC FOR {ip} ---")
    
    request = factory.get('/')
    request.META['REMOTE_ADDR'] = ip
    
    # Check initial state
    print(f"Initially Locked? {check_ip_lockout(request)}")
    
    # 2. Record 5 failures
    for i in range(5):
        print(f"Recording failure {i+1}...")
        record_login_failure(request)
    
    # 3. Final check
    is_locked = check_ip_lockout(request)
    print(f"\nResult: Is IP {ip} locked? {is_locked}")
    
    if is_locked:
        print("✅ SUCCESS: The logic is airtight. IP-based lockout triggers.")
    else:
        print("❌ FAILURE: Logic error.")

if __name__ == "__main__":
    test_hardened_logic()
