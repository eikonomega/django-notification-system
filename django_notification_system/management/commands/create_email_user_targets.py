# TODO: Justin - will need to import User in such a way as to pick up custom user models.
# Here, and anywhere else User is referenced.
# https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#reusable-apps-and-auth-user-model
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from ...models import Target, UserTarget

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

        # This is being called in case this command is run before
        # the email target has been created.
        Target.objects.get_or_create(name="Email", notification_creator_module="Email")

        all_users = User.objects.all()

        for user in all_users:
            # Calling this will create an email user target for each user.
            UserTarget.reset_email_target(user)
