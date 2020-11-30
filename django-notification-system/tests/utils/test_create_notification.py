from django.contrib.auth.models import User
from django.test.testcases import TestCase
from django.utils import timezone

from website.notifications.models import (
    Notification, Target, UserTarget, OptOut)
from website.notifications.utils.notifications_creators import (
    create_expo_notifications)


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

        self.target = Target.objects.create(
            name='Expo',
            class_name='Expo')
        self.user_target1 = UserTarget.objects.create(
            user=self.user_with_targets,
            target=self.target,
            user_target_id='291747127401',
            user_target_friendly_name='Happy Phone')

        self.user_target2 = UserTarget.objects.create(
            user=self.user_with_targets,
            target=self.target,
            user_target_id='92369ryweifwe',
            user_target_friendly_name='Happier Phone')

    def test_successfully_create_expo_notificationss(self):
        """
        This test checks that notifications are created for all
        user targets associated with the user.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        create_expo_notifications(self.user_with_targets,
                                  "Wow",
                                  "You really did it!",
                                  timezone.now())

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 2)

    def test_successfully_create_expo_notif_w_opt_out(self):
        """
        This test checks that notifications are created for all
        user targets associated with the user.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        OptOut.objects.create(user=self.user_with_targets)

        create_expo_notifications(self.user_with_targets,
                                  "Wow",
                                  "You really did it!",
                                  timezone.now())

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 2)

    def test_no_notifications_created__no_target(self):
        """
        If a user has no targets then no notifications can
        be created.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        create_expo_notifications(self.user_without_target,
                                  "Wow",
                                  "You really did it!",
                                  timezone.now())

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 0)

    def test_no_notifications_created__opt_out(self):
        """
        This test checks that notifications are created for all
        user targets associated with the user.
        """
        pre_function_notifications = Notification.objects.all()
        self.assertEqual(len(pre_function_notifications), 0)

        OptOut.objects.create(user=self.user_with_targets, has_opted_out=True)

        create_expo_notifications(self.user_with_targets,
                                  "Wow",
                                  "You really did it!",
                                  timezone.now())

        post_function_notifications = Notification.objects.all()
        self.assertEqual(len(post_function_notifications), 0)
