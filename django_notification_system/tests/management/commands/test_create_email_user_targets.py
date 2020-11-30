from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from six import StringIO

from website.notifications.management.commands.create_email_user_targets import Command
from website.notifications.models import Target, UserTarget

cmd = Command()


class TestCommand(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Danglesauce",
            email="danglesauce@gmail.com",
            first_name="Dangle",
            last_name="Sauce",
            password="ImpressivePassword")

    def test_create_email_user_targets(self):
        """
        Ensure command is functioning correctly.
        """
        # Delete UserTarget from initial signal.
        UserTarget.objects.all().delete()

        pre_call = UserTarget.objects.all()
        self.assertEqual(len(pre_call), 0)

        out = StringIO()
        call_command('create_email_user_targets', stdout=out)

        post_call = UserTarget.objects.all()
        self.assertEqual(len(post_call), 1)

        for target in post_call:
            if target.user == self.user:
                self.assertEqual(target.user_target_id,
                                 self.user.email)
