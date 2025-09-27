"""
Management command to create UserProfile instances for users that don't have them.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from supplies.models import UserProfile


class Command(BaseCommand):
    help = 'Create UserProfile instances for users that do not have them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--default-role',
            type=str,
            default='CUSTOMER',
            choices=['MANAGER', 'CUSTOMER'],
            help='Default role to assign to users without profiles (default: CUSTOMER)'
        )

    def handle(self, *args, **options):
        default_role = options['default_role']
        users_without_profile = User.objects.filter(profile__isnull=True)
        
        if not users_without_profile.exists():
            self.stdout.write(
                self.style.SUCCESS('All users already have profiles.')
            )
            return

        created_count = 0
        for user in users_without_profile:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': default_role}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    f'Created profile for user "{user.username}" with role "{default_role}"'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} user profiles.'
            )
        )