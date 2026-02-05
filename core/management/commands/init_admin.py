from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Initialize admin profile'

    def handle(self, *args, **kwargs):
        try:
            admin_user = User.objects.get(username='admin')
            # Set password
            admin_user.set_password('admin123')
            admin_user.save()
            
            # Create or get profile
            profile, created = UserProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'role': 'admin',
                    'phone': '1234567890',
                    'room_no': 'Admin'
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS('Admin profile created successfully'))
            else:
                self.stdout.write(self.style.SUCCESS('Admin profile already exists'))
                
            self.stdout.write(self.style.SUCCESS(f'Admin credentials: username=admin, password=admin123'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user not found. Please create superuser first.'))
