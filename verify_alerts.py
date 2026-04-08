import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formulad_workshop.settings')
django.setup()

from django.contrib.auth.models import User
from workshop.auth_views import send_titan_security_alert
from django.test import RequestFactory

# 1. Mock Request & User
factory = RequestFactory()
request = factory.get('/login/')
request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'
request.META['REMOTE_ADDR'] = '192.168.1.12'

user = User(username='Rijas')

# 2. Trigger Alert
print("\n--- SIMULATING TITAN SECURITY BROADCAST ---")
send_titan_security_alert(user, request)
print("--- END SIMULATION ---\n")
