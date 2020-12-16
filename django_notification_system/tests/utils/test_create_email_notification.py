
from django.contrib.auth.models import User
from django.test.testcases import TestCase


from django_notification_system.models import (
    Notification, NotificationTarget, TargetUserRecord)
from django_notification_system.notification_creators.email import (
    create_notification)


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

        self.target, created = NotificationTarget.objects.get_or_create(
            name='Email',
            notification_module_name='email'
        )

        self.target_user_record = TargetUserRecord.objects.create(
            user=self.user_with_targets,
            target=self.target,
            target_user_id='sadboi@gmail.com',
            description="Sad Boi's Email",
            active=True
        )

    def test_successfully_create_notifications(self):
        """
        This test checks that email notifications are created for all
        email user targets associated with the user.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        create_notification(
            user=self.user_with_targets,
            title="Hi.",
            body="Hello there, friend.")

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 1)
