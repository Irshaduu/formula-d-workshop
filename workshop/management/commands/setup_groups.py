from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Sets up user groups for Workers and Admins'

    def handle(self, *args, **kwargs):
        # Create Workers group
        workers, created = Group.objects.get_or_create(name='Workers')
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created "Workers" group'))
        else:
            self.stdout.write('   "Workers" group already exists')
        
        # Create Admins group
        admins, created = Group.objects.get_or_create(name='Admins')
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created "Admins" group'))
        else:
            self.stdout.write('   "Admins" group already exists')
        
        self.stdout.write(self.style.SUCCESS('\n✅ User groups setup complete!'))
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Go to Django admin: /admin/auth/user/')
        self.stdout.write('2. Add users to appropriate groups')
        self.stdout.write('3. Workers: Limited access (no price visibility)')
        self.stdout.write('4. Admins: Full access (see prices, invoices)')
