import os
from django.test import Client
from django.urls import reverse

def test_pw_lockout():
    client = Client()
    url = reverse('admin_login')
    
    print("Testing Password Brute-Force Lockout...")
    for i in range(1, 7):
        # Using a dummy password to trigger failure
        response = client.post(url, {'username': 'Sahad', 'password': f'wrong_{i}'}, follow=True)
        content = response.content.decode()
        
        if "Lockout" in content or "blocked" in content:
            print(f"✅ SUCCESS: Lockout triggered at attempt {i}.")
            import re
            match = re.search(r"Lockout|blocked", content)
            if match:
                print(f"Message: Security Lockout detected.")
            return
        else:
            print(f"Attempt {i}: Still allowed (as expected for < 5).")

    print("❌ FAIL: Lockout not triggered after 6 attempts.")

if __name__ == "__main__":
    test_pw_lockout()

