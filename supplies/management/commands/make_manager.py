"""
Management command to make a user a manager.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from supplies.models import UserProfile


class Command(BaseCommand):
    help = 'Make a user a manager'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to make manager')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')

        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if profile.role == 'MANAGER':
            self.stdout.write(
                self.style.WARNING(f'User "{username}" is already a manager.')
            )
        else:
            profile.role = 'MANAGER'
            profile.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully made "{username}" a manager.')
            )