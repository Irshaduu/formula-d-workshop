from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """
    Checks if a user belongs to a specific group.
    Usage in template: {% if request.user|has_group:"Owner" %}
    """
    if not user.is_authenticated:
        return False
        
    # Handling superusers (treat them as having all roles for convenience)
    if user.is_superuser:
        return True
        
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return False
        
    return group in user.groups.all()
