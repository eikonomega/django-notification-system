
from django.contrib.auth.models import User
from django.test.testcases import TestCase


from website.notifications.models import (
    Notification, Target, UserTarget)
from website.notifications.utils.notifications_creators import (
    create_email_notifications)


class TestCreateEmailNotification(TestCase):
    def setUp(self):
        self.user_with_targets = User.objects.create_user(
            username='sadboi@gmail.com',
            email='sadboi@gmail.com',
            first_name='Sad',
            last_name='Boi',
            password='Ok.')

        self.user_without_target = User.objects.create_user(
            username='skeeter@gmail.com',
            email='skeeter@gmail.com',
            first_name='Skeeter',
            last_name='Skeetington',
            password='Sure.')

        # We call this to create the email user_target.
        self.user_with_targets.save()

    def test_successfully_create_notifications(self):
        """
        This test checks that email notifications are created for all
        email user targets associated with the user.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        create_email_notifications(
            user=self.user_with_targets,
            title="Hi.",
            template_path=(
                "user_signup/emails/survey_repetition.html"))

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 1)
