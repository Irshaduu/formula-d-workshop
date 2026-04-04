from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.utils.crypto import get_random_string
from decouple import config
import time
from datetime import timedelta
from django.utils import timezone
from .models import UserSession, FailedAttempt


# ============================================================
# Phone Number Normalization (Last 10 Digits Matching)
# Matches +91, spaces, and different formats in .env vs input.
# ============================================================
def normalize_phone(phone_str):
    """Keep only the last 10 digits to match Indian mobile numbers consistently."""
    if not phone_str:
        return ""
    digits = "".join(filter(str.isdigit, phone_str))
    return digits[-10:] if len(digits) >= 10 else digits

# ============================================================
# Owner Mobile Number Lookup (from .env — developer-registered)
# ============================================================
def get_owner_mobile(identifier):
    """
    Returns the mobile number for the given identifier (can be username or mobile).
    Checks against the owner map in .env.
    """
    owner_map = {
        config('OWNER_1_USERNAME', default='').strip(' ='): config('OWNER_1_MOBILE', default='').strip(' ='),
        config('OWNER_2_USERNAME', default='').strip(' ='): config('OWNER_2_MOBILE', default='').strip(' ='),
    }
    
    # 1. Check if identifier is a registered username
    if identifier in owner_map:
        return owner_map[identifier]
    
    # 2. Check if identifier is a registered mobile number (using normalization)
    target = normalize_phone(identifier)
    for username, mobile in owner_map.items():
        if target == normalize_phone(mobile) and mobile != '':
            return mobile
            
    return None

def get_owner_username_by_mobile(mobile_number):
    """Returns the username associated with a mobile number in .env."""
    target = normalize_phone(mobile_number)
    owner_map = {
        config('OWNER_1_USERNAME', default='').strip(' ='): config('OWNER_1_MOBILE', default='').strip(' ='),
        config('OWNER_2_USERNAME', default='').strip(' ='): config('OWNER_2_MOBILE', default='').strip(' ='),
    }
    for username, mobile in owner_map.items():
        if target == normalize_phone(mobile) and mobile != '':
            return username
    return None


# ============================================================
# Phone Masking (Privacy & Feedback)
# Returns e.g. +91 ******7978
# ============================================================
def mask_phone(phone_str):
    if not phone_str:
        return "****"
    # Keep last 4 digits
    last_four = phone_str[-4:]
    return f"*******{last_four}"


# ============================================================
# IP-Based Lockout Infrastructure (Steel Gate)
# ============================================================
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_ip_lockout(request):
    """Returns True if the IP is currently blocked."""
    ip = get_client_ip(request)
    attempt = FailedAttempt.objects.filter(ip_address=ip).first()
    if attempt and attempt.failures >= 5:
        # 15 Minute window
        lockout_expiry = attempt.last_attempt + timedelta(minutes=15)
        if timezone.now() < lockout_expiry:
            return True
        else:
            # Lockout expired — reset
            attempt.failures = 0
            attempt.save()
    return False

def record_login_failure(request):
    ip = get_client_ip(request)
    attempt, created = FailedAttempt.objects.get_or_create(ip_address=ip)
    attempt.failures += 1
    attempt.save()

def reset_login_failures(request):
    ip = get_client_ip(request)
    FailedAttempt.objects.filter(ip_address=ip).update(failures=0)


# ============================================================
# SMS Function — prints to terminal (replace with Twilio later)
# ============================================================
def send_otp_sms(mobile_number, otp):
    print(f"=========================================")
    print(f"[MOCK SMS] TO: {mobile_number} | OTP: {otp}")
    print(f"=========================================")


# ============================================================
# Security Alert — Notify the OTHER owner about a login
# ============================================================
def send_owner_login_alert(user, request):
    """
    If Sahad logs in, notify Rijas. If Rijas logs in, notify Sahad.
    Includes device info and IP for immediate verification.
    """
    owner1_u = config('OWNER_1_USERNAME', default='').strip()
    owner2_u = config('OWNER_2_USERNAME', default='').strip()
    
    current_username = user.username
    target_mobile = None
    other_owner_name = ""
    
    if current_username == owner1_u:
        target_mobile = config('OWNER_2_MOBILE', default='').strip()
        other_owner_name = config('OWNER_2_USERNAME', default='Assistant Owner')
    elif current_username == owner2_u:
        target_mobile = config('OWNER_1_MOBILE', default='').strip()
        other_owner_name = config('OWNER_1_USERNAME', default='Main Owner')
    
    if target_mobile:
        # Get Device Info
        ua = request.META.get('HTTP_USER_AGENT', 'Unknown Device')
        device_name = UserSession.get_device_name(ua)
        ip = request.META.get('REMOTE_ADDR', 'Unknown IP')
        
        # 2. Build Message
        msg = (
            f"🛡️ SECURITY ALERT: {current_username} just logged into HQ Portal.\n"
            f"📱 Device: {device_name}\n"
            f"🌐 IP: {ip}\n"
            f"If this wasn't expected, REVOKE access now from your dashboard!"
        )
        
        print(f"=========================================")
        print(f"[SECURITY ALERT SMS] TO: {target_mobile} ({other_owner_name})")
        print(f"{msg}")
        print(f"=========================================")


def send_staff_login_alert(user, request):
    """
    When any staff (Office/Floor) logs in, notify BOTH owners.
    """
    owner1_mobile = config('OWNER_1_MOBILE', default='').strip()
    owner2_mobile = config('OWNER_2_MOBILE', default='').strip()
    
    # Get Device Info
    ua = request.META.get('HTTP_USER_AGENT', 'Unknown Device')
    device_name = UserSession.get_device_name(ua)
    ip = request.META.get('REMOTE_ADDR', 'Unknown IP')
    
    role = "Staff"
    if user.groups.filter(name='Office').exists():
        role = "Office"
    elif user.groups.filter(name='Floor').exists():
        role = "Floor"

    msg = (
        f"📋 TEAM ALERT: {user.username} ({role}) just logged in.\n"
        f"📱 Device: {device_name}\n"
        f"🌐 IP: {ip}"
    )

    for mobile in [owner1_mobile, owner2_mobile]:
        if mobile:
            print(f"=========================================")
            print(f"[STAFF LOGIN ALERT] TO OWNER: {mobile}")
            print(f"{msg}")
            print(f"=========================================")


# ============================================================
# Staff Login — Floor & Office only
# ============================================================
def staff_login_view(request):
    """
    Standard login for Floor and Office staff.
    """
    if request.user.is_authenticated:
        return redirect('home')

    # 1. IP Lockout Check
    if check_ip_lockout(request):
        messages.error(request, "🛡️ Security Lockout: Too many failed attempts. Please wait 15 minutes.")
        return render(request, 'workshop/auth/login.html')

    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '').strip()
        user = authenticate(request, username=u, password=p)

        if user is not None:
            # Block owners from staff portal (Generic Error for security)
            if user.groups.filter(name='Owner').exists() or user.is_superuser:
                record_login_failure(request)
                messages.error(request, "Invalid credentials.")
                return redirect('login')

            auth_login(request, user)
            reset_login_failures(request)
            
            # --- Team Security Alert ---
            send_staff_login_alert(user, request)
            return redirect('home')
        else:
            record_login_failure(request)
            messages.error(request, "Invalid credentials.")

    return render(request, 'workshop/auth/login.html')


# ============================================================
# Admin Login — Owner 2FA Step 1 (Password)
# ============================================================
def admin_login_view(request):
    """
    Step 1 of Owner 2FA (Password).
    """
    if request.user.is_authenticated:
        return redirect('home')

    # 1. IP Lockout Check (Steel Gate)
    if check_ip_lockout(request):
        messages.error(request, "🛡️ Security Lockout: Too many failed attempts. Please wait 15 minutes.")
        return render(request, 'workshop/auth/admin_login.html')

    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '').strip()
        
        login_username = u
        norm_u = normalize_phone(u)
        if len(norm_u) == 10:
            resolved_u = get_owner_username_by_mobile(u)
            if resolved_u:
                login_username = resolved_u
        
        user = authenticate(request, username=login_username, password=p)

        if user is not None:
            # Must be an Owner or superuser
            if not (user.groups.filter(name='Owner').exists() or user.is_superuser):
                record_login_failure(request)
                messages.error(request, "Invalid credentials.")
                return redirect('admin_login')

            mobile = get_owner_mobile(login_username)
            if not mobile:
                messages.error(request, "Invalid credentials.")
                return redirect('admin_login')

            # Generate OTP
            otp = get_random_string(length=6, allowed_chars='0123456789')

            request.session['pre_2fa_user_id'] = user.id
            request.session['2fa_otp'] = otp
            request.session['2fa_expire'] = time.time() + 300
            request.session['masked_phone'] = mask_phone(mobile)
            
            send_otp_sms(mobile, otp)
            return redirect('otp_verify')
        else:
            record_login_failure(request)
            messages.error(request, "Invalid credentials.")
            return redirect('admin_login')

    return render(request, 'workshop/auth/admin_login.html')


# ============================================================
# OTP Verify — Owner 2FA Step 2 (OTP)
# ============================================================
def otp_verify_view(request):
    """
    Step 2 of Owner 2FA (OTP).
    """
    user_id = request.session.get('pre_2fa_user_id')
    stored_otp = request.session.get('2fa_otp')
    expire_time = request.session.get('2fa_expire')

    if check_ip_lockout(request):
        messages.error(request, "🛡️ Security Lockout: Too many failed attempts. Please wait 15 minutes.")
        return render(request, 'workshop/auth/admin_login.html')

    if not all([user_id, stored_otp, expire_time]):
        messages.error(request, "Invalid credentials.")
        return redirect('admin_login')

    if time.time() > expire_time:
        messages.error(request, "OTP expired (5 minutes). Please log in again.")
        # Clean up
        for key in ('pre_2fa_user_id', '2fa_otp', '2fa_expire'):
            request.session.pop(key, None)
        return redirect('admin_login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()

        # Track failed attempts
        attempts = request.session.get('2fa_attempts', 0)

        if entered_otp == stored_otp:
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            auth_login(request, user)
            reset_login_failures(request) # Success!

            # --- Collaborative Security Alert ---
            send_owner_login_alert(user, request)
            # ---------------------------

            # Clean up session
            for key in ('pre_2fa_user_id', '2fa_otp', '2fa_expire', '2fa_attempts', 'masked_phone'):
                request.session.pop(key, None)

            messages.success(request, f"Welcome back, {user.username}! ✅")
            return redirect('home')
        else:
            record_login_failure(request)
            attempts += 1
            request.session['2fa_attempts'] = attempts
            remaining = 3 - attempts

            if attempts >= 3:
                for key in ('pre_2fa_user_id', '2fa_otp', '2fa_expire', '2fa_attempts', 'masked_phone'):
                    request.session.pop(key, None)
                messages.error(request, "🛡️ Too many wrong attempts. HQ Access blocked.")
                return redirect('admin_login')
            else:
                messages.error(request, f"Incorrect OTP. {remaining} attempt(s) remaining.")

    context = {
        'masked_phone': request.session.get('masked_phone', 'your registered device')
    }
    return render(request, 'workshop/auth/otp_verify.html', context)


# ============================================================
# Forgot Password — Step 1: Enter Username → Send OTP
# ============================================================
def owner_forgot_password_view(request):
    """
    Owner enters their username.
    System looks up their mobile from .env and sends a reset OTP.
    """
    if request.user.is_authenticated:
        return redirect('home')

    # Check for active lockout from too many wrong OTP attempts
    blocked_until = request.session.get('pwd_reset_blocked_until')
    if blocked_until:
        remaining_secs = blocked_until - time.time()
        if remaining_secs > 0:
            remaining_mins = int(remaining_secs // 60) + 1
            messages.error(request, f"Too many failed attempts. Please wait {remaining_mins} minute(s) before trying again.")
            return render(request, 'workshop/auth/forgot_password.html')
        else:
            request.session.pop('pwd_reset_blocked_until', None)

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()

        # Identification Logic
        target_username = identifier
        norm_id = normalize_phone(identifier)
        if len(norm_id) == 10:
            resolved = get_owner_username_by_mobile(identifier)
            if resolved:
                target_username = resolved

        # Validate existence in .env
        mobile = get_owner_mobile(target_username)
        if not mobile:
            messages.error(request, "No Owner account found with that identifier.")
            return redirect('owner_forgot_password')

        # Check the user actually exists in Django
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(username=target_username)
        except User.DoesNotExist:
            messages.error(request, "No Owner account found with that identifier.")
            return redirect('owner_forgot_password')

        # 60-Second Cooldown Check (Prevent SMS Spam)
        last_send = request.session.get('last_otp_send_time')
        if last_send:
            elapsed = time.time() - last_send
            if elapsed < 60:
                remaining = int(60 - elapsed)
                messages.warning(request, f"Please wait {remaining} seconds before requesting another SMS reset.")
                return render(request, 'workshop/auth/forgot_password.html')

        # Generate OTP
        otp = get_random_string(length=6, allowed_chars='0123456789')

        # Store in session
        request.session['pwd_reset_user_id'] = user.id
        request.session['pwd_reset_otp'] = otp
        request.session['pwd_reset_expire'] = time.time() + 300  # 5 minutes
        request.session['last_otp_send_time'] = time.time() # Update cooldown

        # Send OTP
        send_otp_sms(mobile, otp)

        messages.success(request, "OTP sent to your registered mobile number.")
        return redirect('owner_reset_password')

    return render(request, 'workshop/auth/forgot_password.html')


# ============================================================
# Forgot Password — Step 2: Enter OTP + New Password
# ============================================================
def owner_reset_password_view(request):
    """
    Owner enters the OTP and their new password.
    """
    user_id = request.session.get('pwd_reset_user_id')
    stored_otp = request.session.get('pwd_reset_otp')
    expire_time = request.session.get('pwd_reset_expire')

    if not all([user_id, stored_otp, expire_time]):
        messages.error(request, "Session expired. Please start again.")
        return redirect('owner_forgot_password')

    if time.time() > expire_time:
        messages.error(request, "OTP expired. Please request a new one.")
        for key in ('pwd_reset_user_id', 'pwd_reset_otp', 'pwd_reset_expire'):
            request.session.pop(key, None)
        return redirect('owner_forgot_password')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Track failed OTP attempts
        attempts = request.session.get('pwd_reset_attempts', 0)

        if entered_otp != stored_otp:
            attempts += 1
            request.session['pwd_reset_attempts'] = attempts
            remaining = 3 - attempts

            if attempts >= 3:
                # Lockout — wipe reset session but set a 5-minute block
                for key in ('pwd_reset_user_id', 'pwd_reset_otp', 'pwd_reset_expire', 'pwd_reset_attempts'):
                    request.session.pop(key, None)
                request.session['pwd_reset_blocked_until'] = time.time() + 300  # 5-minute block
                messages.error(request, "Too many wrong attempts. You are blocked for 5 minutes.")
                return redirect('owner_forgot_password')
            else:
                messages.error(request, f"Incorrect OTP. {remaining} attempt(s) remaining.")
            return render(request, 'workshop/auth/reset_password.html')

        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, 'workshop/auth/reset_password.html')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'workshop/auth/reset_password.html')

        # All checks passed — update the password
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        user.save()

        # Clean up session
        for key in ('pwd_reset_user_id', 'pwd_reset_otp', 'pwd_reset_expire', 'pwd_reset_attempts'):
            request.session.pop(key, None)

        messages.success(request, "✅ Password changed successfully! Please log in with your new password.")
        return redirect('admin_login')

    return render(request, 'workshop/auth/reset_password.html')

