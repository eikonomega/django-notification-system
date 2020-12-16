from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.utils import timezone

from django_notification_system.models import (
    Notification, NotificationTarget, TargetUserRecord, NotificationOptOut)
from django_notification_system.notification_creators.expo import (
    create_notification)
from django_notification_system.exceptions import UserIsOptedOut, UserHasNoTargetRecords


class TestCreateNotification(TestCase):
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

        self.target, created = NotificationTarget.objects.get_or_create(
            name='Expo',
            notification_module_name='expo')

        self.user_target1 = TargetUserRecord.objects.create(
            user=self.user_with_targets,
            target=self.target,
            target_user_id='291747127401',
            description='Happy Phone')

        self.user_target2 = TargetUserRecord.objects.create(
            user=self.user_with_targets,
            target=self.target,
            target_user_id='92369ryweifwe',
            description='Happier Phone')

    def test_successfully_create_expo_notificationss(self):
        """
        This test checks that notifications are created for all
        user targets associated with the user.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        create_notification(user=self.user_with_targets,
                            title="Wow",
                            body="You really did it!")

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 2)

    def test_successfully_create_expo_notif_w_opt_out(self):
        """
        This test checks that notifications are created for all
        user targets associated with the user.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        NotificationOptOut.objects.create(user=self.user_with_targets)

        create_notification(user=self.user_with_targets,
                            title="Wow",
                            body="You really did it!")

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 2)

    def test_no_notifications_created__no_target(self):
        """
        If a user has no targets then no notifications can
        be created.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        try:
            create_notification(user=self.user_without_target,
                                title="Wow",
                                body="You really did it!")
        except UserHasNoTargetRecords:
            pass

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 0)

    def test_no_notifications_created__opt_out(self):
        """
        This test checks that notifications are created for all
        user targets associated with the user.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        NotificationOptOut.objects.create(user=self.user_with_targets, active=True)

        try:
            create_notification(user=self.user_with_targets,
                                title="Wow",
                                body="You really did it!")
        except UserIsOptedOut:
            pass

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 0)
