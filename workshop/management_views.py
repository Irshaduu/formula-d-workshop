from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from .decorators import owner_required, office_required
from .models import Mechanic


@office_required
def manage_dashboard(request):
    """
    Central hub for the Owner to manage all staff accounts and mechanics.
    """
    office_group = Group.objects.filter(name='Office').first()
    floor_group = Group.objects.filter(name='Floor').first()
    
    office_users = list(User.objects.filter(groups=office_group)) if office_group else []
    floor_users = list(User.objects.filter(groups=floor_group)) if floor_group else []
    mechanics = Mechanic.objects.all().order_by('name')
    
    return render(request, 'workshop/manage/manage_dashboard.html', {
        'office_users': office_users,
        'floor_users': floor_users,
        'mechanics': mechanics,
    })


@office_required
def manage_create_user(request):
    """
    Create a new Office or Floor staff account.
    Owner sets the username, password, and role.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        role = request.POST.get('role', '')
        
        if not username or not password or role not in ['Office', 'Floor']:
            messages.error(request, "All fields are required. Role must be Office or Floor.")
            return redirect('manage_dashboard')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken. Choose another.")
            return redirect('manage_dashboard')
        
        if len(password) < 4:
            messages.error(request, "Password must be at least 4 characters.")
            return redirect('manage_dashboard')
        
        user = User.objects.create_user(username=username, password=password)
        group = Group.objects.get(name=role)
        user.groups.add(group)
        user.save()
        messages.success(request, f"✅ {role} account '{username}' created successfully!")
    
    return redirect('manage_dashboard')


@office_required
def manage_reset_password(request, user_id):
    """
    Reset the password for an Office or Floor staff account.
    """
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        
        # Safety: prevent owners from editing other owner/superuser accounts here
        if user.groups.filter(name='Owner').exists() or user.is_superuser:
            messages.error(request, "Cannot modify Owner accounts from this panel.")
            return redirect('manage_dashboard')
        
        new_password = request.POST.get('new_password', '').strip()
        if not new_password or len(new_password) < 4:
            messages.error(request, "Password must be at least 4 characters.")
            return redirect('manage_dashboard')
        
        user.set_password(new_password)
        user.save()
        messages.success(request, f"✅ Password for '{user.username}' has been reset.")
    
    return redirect('manage_dashboard')


@office_required
def manage_delete_user(request, user_id):
    """
    Delete an Office or Floor staff account.
    """
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        
        if user.groups.filter(name='Owner').exists() or user.is_superuser:
            messages.error(request, "Cannot delete Owner accounts from this panel.")
            return redirect('manage_dashboard')
        
        username = user.username
        user.delete()
        messages.success(request, f"✅ Account '{username}' has been deleted.")
    
    return redirect('manage_dashboard')


@office_required
def manage_create_mechanic(request):
    """
    Add a new Mechanic to the workshop roster.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip().title()  # Auto-capitalize name
        
        if not name:
            messages.error(request, "Mechanic name cannot be empty.")
            return redirect('manage_dashboard')
        
        if Mechanic.objects.filter(name__iexact=name).exists():
            messages.error(request, f"Mechanic '{name}' already exists in the roster.")
            return redirect('manage_dashboard')
        
        Mechanic.objects.create(name=name)
        messages.success(request, f"✅ Mechanic '{name}' added to the roster!")
    
    return redirect('manage_dashboard')


@office_required
def manage_toggle_mechanic(request, mechanic_id):
    """
    Toggle a mechanic's active/retired status.
    """
    if request.method == 'POST':
        mechanic = get_object_or_404(Mechanic, pk=mechanic_id)
        mechanic.is_active = not mechanic.is_active
        mechanic.save()
        status = "activated" if mechanic.is_active else "deactivated"
        messages.success(request, f"✅ Mechanic '{mechanic.name}' has been {status}.")
    
    return redirect('manage_dashboard')


@office_required
def manage_edit_mechanic(request, mechanic_id):
    """
    Rename a mechanic in the roster.
    """
    if request.method == 'POST':
        mechanic = get_object_or_404(Mechanic, pk=mechanic_id)
        new_name = request.POST.get('name', '').strip().title()

        if not new_name:
            messages.error(request, "Mechanic name cannot be empty.")
            return redirect('manage_dashboard')

        if Mechanic.objects.filter(name__iexact=new_name).exclude(pk=mechanic_id).exists():
            messages.error(request, f"A mechanic named '{new_name}' already exists.")
            return redirect('manage_dashboard')

        old_name = mechanic.name
        mechanic.name = new_name
        mechanic.save()
        messages.success(request, f"✅ Mechanic renamed from '{old_name}' to '{new_name}'.")

    return redirect('manage_dashboard')
