import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp


class Command(BaseCommand):
    help = 'Set up a Site and Google SocialApp in the database'

    def handle(self, *args, **options):

        site_id = getattr(settings, 'SITE_ID', 1)

        # Environment variables for Site
        site_domain = os.getenv('SITE_DOMAIN', 'example.com')
        site_name = os.getenv('SITE_NAME', 'Example')

        # Environment variables for Google SocialApp
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        google_secret_key = os.getenv('GOOGLE_SECRET_KEY')

        try:
            # Set up or update the Site
            site, created = Site.objects.update_or_create(
                id=site_id,
                defaults={
                    'domain': site_domain,
                    'name': site_name
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Site with ID {site_id} \
                        created: {site_domain} ({site_name})'))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f'Site with ID {site_id}\
                        updated: {site_domain} ({site_name})'))

            # Set up or update the Google SocialApp
            social_app, created = SocialApp.objects.update_or_create(
                provider='google',
                defaults={
                    'name': 'Google',
                    'client_id': google_client_id,
                    'secret': google_secret_key
                }
            )
            # Link SocialApp to the Site
            social_app.sites.set([site])

            if created:
                self.stdout.write(self.style.SUCCESS(
                    'Google SocialApp created and linked to the site.'))
            else:
                self.stdout.write(self.style.SUCCESS(
                    'Google SocialApp updated and linked to the site.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
