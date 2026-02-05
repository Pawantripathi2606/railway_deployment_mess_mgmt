from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import UserProfile


class Command(BaseCommand):
    help = 'Create a test user for testing user features'

    def handle(self, *args, **kwargs):
        # Create test user
        username = 'testuser'
        password = 'test123'
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
        else:
            user = User.objects.create_user(
                username=username,
                email='testuser@mess.com',
                password=password,
                first_name='Test',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        
        # Create or update profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'user',
                'phone': '9876543210',
                'room_no': '101'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created profile for {username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Profile already exists for {username}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Test user credentials:'))
        self.stdout.write(self.style.SUCCESS(f'   Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'   Password: {password}'))
