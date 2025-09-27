"""
Management command to create an admin superuser with a profile.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from supplies.models import UserProfile
import getpass


class Command(BaseCommand):
    help = 'Create an admin superuser with manager profile'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username')
        parser.add_argument('--email', type=str, help='Admin email')
        parser.add_argument('--no-input', action='store_true', help='Create with default values')

    def handle(self, *args, **options):
        if options['no_input']:
            username = options.get('username', 'admin')
            email = options.get('email', 'admin@example.com')
            password = 'admin123'
        else:
            username = options.get('username') or input('Username: ')
            email = options.get('email') or input('Email: ')
            password = getpass.getpass('Password: ')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User "{username}" already exists.')
            )
            return

        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        # Create or update profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'MANAGER'}
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created admin user "{username}" with manager profile.'
            )
        )
        
        if options['no_input']:
            self.stdout.write(
                self.style.WARNING(
                    f'Default credentials: username="{username}", password="admin123"'
                )
            )