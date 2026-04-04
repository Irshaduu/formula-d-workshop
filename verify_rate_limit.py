import os
import sys
import time
from django.test import Client
from django.urls import reverse

def test_sms_cooldown():
    client = Client()
    
    # 1. Test Forgot Password Cooldown
    print("Testing Forgot Password Cooldown Step 1...")
    # Using 'Sahad' which we verified in .env
    response1 = client.post(reverse('owner_forgot_password'), {'username': 'Sahad'})
    
    if response1.status_code == 302: # Redirect to reset password
        print("✅ SUCCESS: First OTP sent.")
    else:
        print(f"❌ FAIL: First OTP not sent. Status: {response1.status_code}")
        # print(response1.content.decode())
        return

    # Second request immediately
    print("\nTesting Forgot Password Cooldown Step 2 (Immediate)...")
    response2 = client.post(reverse('owner_forgot_password'), {'username': 'Sahad'}, follow=True)
    
    content = response2.content.decode()
    if "wait" in content and ("seconds" in content or "minute" in content):
        print("✅ SUCCESS: Rate-limiting caught the second request.")
        # Find the exact message for confirmation
        import re
        match = re.search(r"Please wait \d+ seconds", content)
        if match:
            print(f"Captured Message: {match.group(0)}")
    else:
        print("❌ FAIL: Rate-limiting DID NOT catch the second request.")
        # print(content) # Debug

if __name__ == "__main__":
    test_sms_cooldown()
