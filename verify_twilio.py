import os
import django
import sys
from decouple import config

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formulad_workshop.settings')
django.setup()

from workshop.auth_views import send_twilio_sms

def test_twilio():
    print("\n--- 🛰️ TITAN TWILIO HANDSHAKE ---")
    
    # 1. Check Config
    sid = config('TWILIO_ACCOUNT_SID', default='your_sid_here')
    if 'your_sid_here' in sid:
        print("❌ ERROR: You haven't updated your .env file with real Twilio keys yet!")
        print("Please edit your .env file and paste your ACCOUNT_SID, AUTH_TOKEN, and FROM_NUMBER.")
        return

    # 2. Ask for Test Number
    target = input("Enter the registered mobile number to test (e.g., +919567494933): ").strip()
    if not target:
        print("❌ No number entered. Aborting.")
        return

    # 3. Send Test
    msg = "🛡️ TITAN SECURITY: This is a live test of your WorkshopOS Alert System. Connection Successful."
    print(f"Attempting to send to {target}...")
    
    success = send_twilio_sms(target, msg)
    
    if success:
        print("\n✅ SUCCESS! Check your phone for the Titan Alert.")
    else:
        print("\n❌ FAILED. Check the errors.log or your Twilio Console for details.")
    
    print("--- END HANDSHAKE ---\n")

if __name__ == "__main__":
    test_twilio()
