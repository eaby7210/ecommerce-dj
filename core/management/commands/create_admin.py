import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create an admin account if it does not exist'

    def handle(self, *args, **options):
        # Fetch variables from environment
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        password = os.getenv('ADMIN_PASSWORD', 'admin123')

        # Get the user model from settings
        User = get_user_model()

        # Check if the username exists
        if not User.objects.filter(username=username).exists():
            # Create the admin user
            User.objects.create_superuser(
                username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(
                f'Admin account "{username}" created successfully!'))
        else:
            self.stdout.write(self.style.WARNING(
                f'Admin account "{username}" already exists.'))
