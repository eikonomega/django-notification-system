"""Django Management Command."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from ...models import TargetUserRecord, NotificationTarget

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

        email_target = NotificationTarget.objects.get(
            name='Email', notification_module_name='email')

        for user in all_users:
            # Calling this will create an email user target for each user.
            if user.email:
                TargetUserRecord.objects.update_or_create(
                    user=user,
                    target=email_target,
                    target_user_id=user.email,
                    defaults={
                        "active": True,
                        "description": f"{user.first_name} {user.last_name}'s Email",
                    },
                )
            else:
                print(f"{user.username} has no email address on record.")