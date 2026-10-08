from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from waste_reports.models import UserProfile


class Command(BaseCommand):
    help = "Create the SizaClean demo Authority and Collector accounts"

    def handle(self, *args, **options):

        # Create Authority account
        authority, created = User.objects.get_or_create(
            username="authority1",
            defaults={
                "email": "authority1@sizaclean.com",
            }
        )

        authority.set_password("Authority123")
        authority.save()

        UserProfile.objects.update_or_create(
            user=authority,
            defaults={"role": "authority"}
        )

        # Create Collector account
        collector, created = User.objects.get_or_create(
            username="collector1",
            defaults={
                "email": "collector1@sizaclean.com",
            }
        )

        collector.set_password("Collector123")
        collector.save()

        UserProfile.objects.update_or_create(
            user=collector,
            defaults={"role": "collector"}
        )

        self.stdout.write(
            self.style.SUCCESS(
                "SizaClean Authority and Collector accounts created successfully."
            )
        )