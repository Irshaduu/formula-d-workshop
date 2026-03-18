from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_user_groups(sender, **kwargs):
    """
    Automatically create the three core Role-Based Access Groups
    if they do not already exist when the app starts.
    """
    from django.contrib.auth.models import Group
    groups = ['Owner', 'Office', 'Floor']
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)

class WorkshopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workshop'

    def ready(self):
        # Register the signal to create groups after migrations
        post_migrate.connect(create_user_groups, sender=self)

