"""Django Management Command."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from ...models import TargetUserRecord

User = get_user_model()


class Command(BaseCommand):
    """
    Create Email UserTargets for all users in the DB.
    """

    help = __doc__

    def handle(self, *args, **options):
        """
        This is what is being run by manage.py
        """
        all_users = User.objects.all()

        for user in all_users:
            # Calling this will create an email user target for each user.
            TargetUserRecord.reset_email_target(user)
